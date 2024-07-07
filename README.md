
# Telegram Statistics Collector

A set of Python scripts that are used to collect and analyze statistics from Telegram group messages. The project consists of two scripts:

- `collect_data.py`: Fetches messages from a specified Telegram group, lookes for keywords and stores various statistics about the messages and their senders in JSON files and a SQLite database. Statistics and keywords are configurable.

- `get_all_words.py`: Fecthes messages from a specified Telegram group and stores all words found into 4 `.json` files. (case sensitive / insensitive; sorted alphabetically / by frequency)

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/ali-albdaer/TelegramStatisticsCollector.git
   ```

2. **Install the required Python packages:**

   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. **Create a `config.py` file in the `res` directory and provide the following data (see `res/config.example.py`):**

   ```python
   # res/config.py
   telegram_user = 'your_telegram_user'
   api_id = 'your_api_id'
   api_hash = 'your_api_hash'
   telegram_phone = 'your_telegram_phone'
   telegram_group_id = 'your_group_id'
   ```

2. **Optionally configure the following parameters:**
   ```python
   # res/config.py
   TOP_PHRASE_LIMIT = 20
   TOP_ACTIVE_DAYS_LIMIT = 10
   GLOBAL_MESSAGE_LIMIT = 30
   GLOBAL_RANKING_LIMIT = 10
   CATEGORY_MENTION_LIMIT = 100

   IGNORE_COMMON_WORDS = True
   SHOW_PROGRESS_BAR = True
   CASE_INSENSITIVE = True
   CONVERT_UNICODE = True
   LOGOUT = False
   ```

3. **Create a `phrases.py` file in the `res` directory and add the words you want to track (see `res/phrases.example.py`):**

   ```python
   # res/phrase.py
   category_sets = {
      'greetings': {'hello', 'hi', 'hey'},
      'farewells': {'bye', 'goodbye'}
      'animals': {'dog', 'cat', 'elephant', 'giraffe'},
      'colors': {'red', 'blue', 'green', 'yellow', 'orange', 'purple'},
      'numbers': set(map(str, range(1001))), 
   }

   ignored_words = {"the", "in", "a", "it", "is", "and", "to", "of", "i", "you"}
   ```

4. **Flag certain words as curse words or implement your custom logic like fuzzy search (see `res/explicit.example.py`):**
   ```python
   # res/explicit.py
   curses = {"slubberdagullion", "gobemouche", "fopdoodle", "tatterdemalion", "scallywag"}
   ```
   
## Usage

1. **Run the script you want:**

   ```sh
   python collect_data.py
   ```

   OR

   ```sh
   python get_all_words.py
   ```

   Either script will connect to your Telegram account and start collecting messages from the specified group. If it's the first time running the script, you will need to authorize the Telegram client. Simply type the code you receive from Telegram in the terminal.

2. **View the data:**
   `collect_data.py`: the statistics will be saved in:
      - `data/global_stats.json`,
      - `data/user_stats.json`,
      - and `data/user_stats.db`.

   `get_all_words.py`: the words will be saved in:
      - `'data/all_words_case_sensitive_freq.json'`, 
      - `'data/all_words_case_sensitive_alpha.json'`,
      - `'data/all_words_case_insensitive_freq.json'`,
      - and `'data/all_words_case_insensitive_alpha.json'`.

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
