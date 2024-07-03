
# Telegram Statistics Collector

A Python script to collect and analyze statistics from Telegram group messages. The script fetches messages from a specified Telegram group and stores various statistics about the messages and users in JSON files and a SQLite database.

## Features

- Collects top messages, amount of media, and various user statistics from a Telegram group for each user.
- Tracks ALL CAPS messages and curses.
- Configurable options to ignore common words and display a progress bar.

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/ali-albdaer/TelegramStatisticsCollector.git
   cd telegram-message-stats-collector
   ```

2. **Install the required Python packages:**

   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. **Adjust the `config.py` file and provide the following data:**

   ```python
   # config.py
   telegram_user = 'your_telegram_user'
   api_id = 'your_api_id'
   api_hash = 'your_api_hash'
   telegram_phone = 'your_telegram_phone'
   telegram_group_id = 'your_group_id'
   ```

2. **Optionally configure the following parameters:**
   ```python
   TOP_MESSAGE_LIMIT = 20
   TOP_ACTIVE_DAYS_LIMIT = 10
   GLOBAL_MESSAGE_LIMIT = 30
   GLOBAL_RANKING_LIMIT = 10
   CATEGORY_MENTION_LIMIT = 100

   IGNORE_COMMON_WORDS = True
   SHOW_PROGRESS_BAR = True
   CASE_INSENSITIVE = True
   ```

3. **Add the words you want to track to the `lookup.py` file:**

   ```python
   # lookup.py
   category_sets = {
       # Example category sets
       'greetings': {'hello', 'hi', 'hey'},
       'farewells': {'bye', 'goodbye', 'see you'}
   }

   ignored_words = {"the", "in", "a", "it", "is", "and", "to", "of", "i", "you"}

   curses = {"slubberdagullion", "gobemouche", "fopdoodle"}
   ```

## Usage

1. **Run the script:**

   ```sh
   python process.py
   ```

   The script will connect to your Telegram account and start collecting messages from the specified group. If it's the first time running the script, you will need to authorize the Telegram client. (Type the code you receive from telegram in the terminal)

2. **View the statistics:**

   - The global statistics will be saved in `data/global_stats.json`.
   - The user statistics will be saved in `data/user_stats.json` and `data/user_stats.db`.


## Disclaimer
This project was created for fun and educational purposes. Please use it responsibly and ethically. I do not support any malicious use of this script, including but not limited to:

- Spying on individuals without their consent.
- Collecting data for harassment or abuse.
- Violating Telegram's terms of service or privacy policies.

By using this project, you agree to use it only for lawful and ethical purposes.

## Contributing

You are more than welcome to contribute to this project! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
