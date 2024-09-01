# KickChatBot

KickChatBot is a Python-based bot that interacts with a livestream chat using Selenium and OpenAI's GPT-4. The bot monitors the chat, extracts recent messages to create a chat context, and generates funny follow-up messages to send back into the chat.

## Features

- **Automated Chat Interaction:** The bot automatically monitors chat messages, maintaining a context of the latest messages.
- **AI-Powered Message Generation:** Uses OpenAI's GPT-4 to generate contextually relevant and humorous messages to keep the chat lively.
- **Customizable Wait Times:** Adjust the wait time between messages to control the bot's interaction frequency.
- **Flexible Input:** Accepts both streamer usernames and full URLs for Kick.com.

## Prerequisites

Before running this project, ensure you have the following installed:

- [Python 3.7+](https://www.python.org/downloads/)
- [Selenium](https://www.selenium.dev/)
- [Chrome WebDriver](https://sites.google.com/chromium.org/driver/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/KickChatBot.git
   cd KickChatBot
   ```

2. **Install the required Python packages:**

   ```bash
   pip install selenium openai
   ```

3. **Set up Chrome WebDriver:**

   Download and place the [Chrome WebDriver](https://sites.google.com/chromium.org/driver/) in your system's PATH or in the same directory as your script.

4. **Configure User Data Directory:**

   - Set the `user-data-dir` and `profile-directory` options in the script to point to your Chrome profile directory to maintain session data (e.g., logged-in state).

## Usage

1. **Run the script:**

   ```bash
   python KickChatBot.py
   ```

2. **Enter the required information:**

   - **Streamer Identifier:** Enter the Kick streamer's username or full chat URL.
   - **OpenAI API Key:** Provide your OpenAI API key when prompted.

3. **Watch the bot in action:**

   The bot will monitor the chat, generate funny responses based on recent messages, and post them back into the chat. It will automatically continue this process until you manually stop it (e.g., by pressing `Ctrl+C`).

## Configuration

- **MAX_MESSAGES_FOR_CONTEXT:** Defines how many chat messages are used to generate the context for the AI. Default is `10`.
- **MIN_WAIT_TIME and MAX_WAIT_TIME:** Configure the random wait time (in seconds) between sending messages. Default values are `10` and `30` seconds, respectively.

## Example Output

```
Enter the Kick streamer's username or the full URL of their chat page: some_streamer
Waiting for the page to load...
Page loaded.
Enter your OpenAI API key: sk-xxxxxxxxxxxxxxxxxxxx
Waiting for 15 seconds before sending the next message...
Using context: User1: This is awesome\nUser2: I love it\nUser3: Can't stop laughing
Sent message successfully: Keep it going
```

## Limitations

- **Chat Input Field Selector:** The script currently assumes a specific structure for the chat input field and send button in Kick.com's chat UI. If these change, the CSS selectors in the script may need to be updated.
- **Context Size:** Large context sizes may impact the relevance of generated messages. Fine-tuning the `MAX_MESSAGES_FOR_CONTEXT` value may be necessary depending on the chat activity.

## Contributing

Feel free to submit issues or pull requests to improve this project. Contributions are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

