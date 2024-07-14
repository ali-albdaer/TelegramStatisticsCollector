
# Telegram Statistics Collector

A set of Python scripts that collects, analyzes and visualizes statistics from Telegram group messages. The project consists of 3 scripts:

- `collect_data.py`: Fetches messages from a specified Telegram group, lookes for keywords and stores various statistics about the messages and their senders in JSON files and a SQLite database. Statistics and keywords are configurable.

- `get_all_words.py`: Fecthes messages from a specified Telegram group and stores all words found into 4 `.json` files. (case sensitive / insensitive; sorted alphabetically / by frequency)

- `wordcloud-extension/create_wordclouds.py`: Converts the `.json` files that are obtained from `collect_data.py` to word clouds. See [wordclouds extension](#extra-funtionality-wordclouds-experimental)

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

2. **Choose the paths for the output files:**

   ```python
   # res/config.py
   # File paths for collect_data.py
   session_file = f'{telegram_user}.session'
   global_stats_json = 'data/global_stats.json'
   user_stats_json = 'data/user_stats.json'
   user_stats_db = 'data/users.db'

   # File paths for get_all_words.py
   sensitive_freq_json = 'data/all_words_case_sensitive_freq.json'
   sensitive_alpha_json = 'data/all_words_case_sensitive_alpha.json'
   insensitive_freq_json = 'data/all_words_case_insensitive_freq.json'
   insensitive_alpha_json = 'data/all_words_case_insensitive_alpha.json'
   ```

3. **Optionally configure the following parameters:**

   ```python
   # res/config.py
   # Flags
   CONVERT_UNICODE = True
   CASE_INSENSITIVE = True
   IGNORE_COMMON_WORDS = False
   SHOW_PROGRESS_BAR = True
   COUNT_REACTIONS = True
   LOGOUT = False
   GLOBAL_RANKING_BY_RATIO = True

   # Limits
   MIN_WORD_LENGTH = 1

   USER_WORD_LIMIT = 100
   USER_REACTION_LIMIT = 20
   USER_CATEGORY_LIMIT = 10
   USER_ACTIVE_DAYS_LIMIT = 3

   GLOBAL_WORD_LIMIT = 50
   GLOBAL_REACTION_LIMIT = 10 
   GLOBAL_CATEGORY_LIMIT = 1000 
   GLOBAL_RANKING_LIMIT = 50 
   ```

4. **Create an `explicit.py` file in the `res` directory and flag certain words as curse words (see `res/explicit.example.py`):**

   ```python
   # res/explicit.py
   curses = {"slubberdagullion", "gobemouche", "fopdoodle", "tatterdemalion", "scallywag"}
   ```

5. **Create a `phrases.py` file in the `res` directory and add the words/phrases you want to track (see `res/phrases.example.py`):**

   ```python
   # res/phrase.py
   from res.explicit import curses

   category_sets = {
      'animals': {'dog', 'cat', 'elephant', 'giraffe'},
      'colors': {'black', 'white', 'red', 'blue', 'green'},
      'countires'; {('united states', 'usa', 'america'), 'canada', 'mexico'},
      'scientists': {('albert einstein', 'einstein'), ('nicola tesla', 'tesla')},
      'cars': {'bmw', 'toyota', 'tesla'},
      'letters': {'a', 'b', 'c'},
      'numbers': set(map(str, range(1001))), 
      'curses': curses
   }

   ignored_words = {"the", "in", "a", "it", "is", "and", "to", "of", "i", "you"}
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

## Extra Funtionality: Wordclouds (experimental)
You can convert the json data you obtained to nice word clouds, more info can be found in [wordcloud.md](wordcloud-extension/wordcloud.md)

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
