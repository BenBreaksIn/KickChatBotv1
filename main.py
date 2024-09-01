from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
import time
from datetime import datetime
import random
from collections import deque
import difflib

MAX_MESSAGES_FOR_CONTEXT = 10
MIN_WAIT_TIME = 10
MAX_WAIT_TIME = 60
MAX_RECENT_MESSAGES = 5
SIMILARITY_THRESHOLD = 0.9

session_start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

chat_log_file_path = f"chat_logs_{session_start_time}.txt"
error_log_file_path = f"error_logs_{session_start_time}.txt"

processed_messages = set()
recent_messages = deque(maxlen=MAX_RECENT_MESSAGES)
bot_sent_messages = set()


def normalize_text(text):
    return text.lower().strip().replace("'", "").replace('"', '')


def is_message_similar(new_message):
    for msg in recent_messages:
        similarity = difflib.SequenceMatcher(None, new_message, normalize_text(msg)).ratio()
        if similarity > SIMILARITY_THRESHOLD:
            return True
    return False


def clean_generated_message(message):
    unwanted_prefix = "Response: "
    if message.startswith(unwanted_prefix):
        return message[len(unwanted_prefix):]
    return message


def modify_prompt_for_positive_comments_about_nick(context_messages):
    base_prompt = "Based on the chat, create an engaging comment about the stream in the voice of a teen internet troll use no punctuation."
    return "\n".join(context_messages) + "\n" + base_prompt


def send_message_in_chat(driver, message_text, bot_username):
    global bot_sent_messages
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
        bot_sent_messages.add(f"{bot_username}: {normalize_text(message_text)}")
    except Exception as e:
        with open(error_log_file_path, "a", encoding='utf-8') as error_file:
            error_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Error sending message: {e}\n")


def stream_chat(driver, chat_context, bot_username):
    global processed_messages
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#chatroom [data-chat-entry]'))
        )
        chat_messages = driver.find_elements(By.CSS_SELECTOR, '#chatroom [data-chat-entry]')
        for message in chat_messages:
            username_elements = message.find_elements(By.CSS_SELECTOR, '.chat-entry-username')
            message_content_elements = message.find_elements(By.CSS_SELECTOR, '.chat-entry-content')
            if username_elements and message_content_elements:
                username = username_elements[0].text
                message_text = message_content_elements[0].text
                if username == bot_username:
                    continue
                message_key = f"{username}: {normalize_text(message_text)}"
                if message_key not in processed_messages:
                    processed_messages.add(message_key)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    full_message = f"{timestamp} | {username}: {message_text}"
                    print(full_message)
                    with open(chat_log_file_path, "a", encoding='utf-8') as chat_file:
                        chat_file.write(f"{full_message}\n")
                    chat_context.append(normalize_text(message_text))
                    if len(chat_context) > MAX_MESSAGES_FOR_CONTEXT:
                        chat_context.popleft()
    except Exception as e:
        with open(error_log_file_path, "a", encoding='utf-8') as error_file:
            error_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Error updating chat context: {e}\n")


def format_streamer_url(streamer_identifier):
    return f"https://kick.com/{streamer_identifier}" if not streamer_identifier.startswith(
        "http") else streamer_identifier


def main():
    chat_context = deque(maxlen=MAX_MESSAGES_FOR_CONTEXT)
    bot_username = input("Enter the bot's username (This will be used to identify and exclude its messages): ").strip()
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
            wait_time = random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME)
            print(f"Waiting for {wait_time} seconds before collecting messages...")
            time.sleep(wait_time)
            stream_chat(driver, chat_context, bot_username)
            context_messages = list(chat_context)[-MAX_MESSAGES_FOR_CONTEXT:]
            prompt_for_openai = modify_prompt_for_positive_comments_about_nick(context_messages)
            print(f"Prompt for OpenAI: {prompt_for_openai}")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "the following is the live chat log for a live streamer. Create a relevant message based on the chat no longer than 10 words."},
                    *[
                        {"role": "user", "content": message}
                        for message in context_messages
                    ],
                    {"role": "user", "content": prompt_for_openai}
                ]
            )
            generated_message = clean_generated_message(response.choices[0].message.content.strip('"').strip("'"))
            if not is_message_similar(generated_message):
                send_message_in_chat(driver, generated_message, bot_username)
                recent_messages.append(normalize_text(generated_message))
            else:
                print("Generated message is too similar to recent ones; skipping.")
    except KeyboardInterrupt:
        print("Stopping script...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
