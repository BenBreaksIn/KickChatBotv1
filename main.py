###working has uses messages from chat for content to send a response


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
import time
import random
from collections import deque

# Parameters for chat context and timing
MAX_MESSAGES_FOR_CONTEXT = 10
MIN_WAIT_TIME = 10
MAX_WAIT_TIME = 30


def send_message_in_chat(driver, message_text):
    try:
        message_text = ''.join(char for char in message_text if ord(char) <= 0xFFFF)
        chat_input_selector = '#message-input[data-placeholder="Send message..."]'
        send_button_selector = 'button.variant-action.size-md.base-button'
        input_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, chat_input_selector))
        )
        input_field.clear()
        input_field.send_keys(message_text)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, send_button_selector))
        )
        send_button = driver.find_element(By.CSS_SELECTOR, send_button_selector)
        send_button.click()
        print(f"Sent message successfully: {message_text}")
    except Exception as e:
        print(f"Error sending message: {e}")


def stream_chat(driver, chat_context):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#chatroom [data-chat-entry]'))
        )
        chat_messages = driver.find_elements(By.CSS_SELECTOR, '#chatroom [data-chat-entry]')
        for message in chat_messages[-MAX_MESSAGES_FOR_CONTEXT:]:
            username_elements = message.find_elements(By.CSS_SELECTOR, '.chat-entry-username')
            message_content_elements = message.find_elements(By.CSS_SELECTOR, '.chat-entry-content')
            if username_elements and message_content_elements:
                username = username_elements[0].text
                message_text = message_content_elements[0].text
                chat_context.append(f"{username}: {message_text}")
                if len(chat_context) > MAX_MESSAGES_FOR_CONTEXT:
                    chat_context.popleft()
    except Exception as e:
        print(f"Error while updating chat context: {e}")


def format_streamer_url(streamer_identifier):
    return f"https://kick.com/{streamer_identifier}" if not streamer_identifier.startswith(
        "http") else streamer_identifier


def main():
    chat_context = deque(maxlen=MAX_MESSAGES_FOR_CONTEXT)

    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=C:/Users/bgpit/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Profile 12")
    driver = webdriver.Chrome(options=options)
    streamer_identifier = input("Enter the Kick streamer's username or the full URL of their chat page: ").strip()
    streamer_identifier = format_streamer_url(streamer_identifier)
    driver.get(streamer_identifier)
    print("Waiting for the page to load...")
    time.sleep(5)
    print("Page loaded.")

    openai_api_key = input("Enter your OpenAI API key: ").strip()
    client = OpenAI(api_key=openai_api_key)

    try:
        while True:
            stream_chat(driver, chat_context)

            wait_time = random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME)
            print(f"Waiting for {wait_time} seconds before sending the next message...")
            time.sleep(wait_time)

            context_messages = list(chat_context)[-MAX_MESSAGES_FOR_CONTEXT:]
            # Extract and use only the message parts, excluding usernames
            message_texts = [msg.split(': ', 1)[1] if ': ' in msg else msg for msg in context_messages]
            context = "\n".join(message_texts)
            print(f"Using context: {context}")

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "The following is a chat between users in a livestream."},
                          *[
                              {"role": "user", "content": text}
                              for text in message_texts
                          ],
                          {"role": "user",
                           "content": "Generate a short funny follow-up message no longer than 8 words use no punctuation."}]
            )
            generated_message = response.choices[0].message.content.strip('"').strip("'")

            send_message_in_chat(driver, generated_message)
    except KeyboardInterrupt:
        print("Stopping script...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
