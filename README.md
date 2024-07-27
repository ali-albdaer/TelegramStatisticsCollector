
# Telegram Statistics Collector

A set of Python scripts that collects, analyzes and visualizes statistics from Telegram group messages. The project consists of 5 scripts:

- `fetch_group.py`: Fetches messages from the specified group and saves them to a sqlite database. The last processed message is checked when the script is executed, new messages can be easily added to the db by exeuting the script again.

- `collect_data.py`: Analyzes the messages in the db file then saves various statistics about the messages and their senders in 2 JSON files (global_stats and user_stats) and creates an extra SQLite database for users. Statistics and keywords are configurable. Optional sentiment analysis support.

- `get_all_words.py`: Fecthes messages from a specified Telegram group and stores all words found into 4 `.json` files. (case sensitive / insensitive; sorted alphabetically / by frequency).

- `wordcloud-extension/create_wordclouds.py`: Uses the word and category data in the JSON files (obtained from `collect_data.py`) to generate word clouds. See [wordclouds extension](#visualizing-the-data-experimental)

- `graph-extension/create_graphs.py`: Converts user / global metrics (message count, media count, ...) and other analytics into various static graphs and animations. See [graphs extension](#visualizing-the-data-experimental)

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

2. **Optionally configure the rest of the parameters:**

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
   ...

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
   ...

   # Sentiment Analysis Configuration
   ANALYZE_SENTIMENTS = False
   SENTIMENT_PIPELINE_ARGS = ('text-classification', )
   SENTIMENT_PIPELINE_KWARGS = {
      'model': 'j-hartmann/emotion-english-distilroberta-base',
      'top_k': None,
      'truncation': True
   }
   ...

   # File Paths
   user_stats_json = f'{output_folder}/user_stats.json'
   user_stats_db = f'{output_folder}/users.db'
   session_file = f'{telegram_user}.session'
   log_channel_file = f'{output_folder}/channel_log.txt'
   ...
   ```

4. **Create a file called `explicit.py` in the `res` directory and flag certain words as curse words (see `res/explicit.example.py`):**

   ```python
   # res/explicit.py
   curses = {"slubberdagullion", "gobemouche", "fopdoodle", "tatterdemalion", "scallywag"}
   ```

5. **Create a file called `phrases.py` in the `res` directory and add the words/phrases you want to track (see `res/phrases.example.py`):**

   ```python
   # res/phrases.py
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

1. **Run the scripts you want:**

   ```sh
   python fetch_group.py
   python collect_data.py
   ```

   OR

   ```sh
   python get_all_words.py
   ```

   Either set of scripts will connect to your Telegram account and start collecting messages from the specified group. If it's the first time running the script, you will need to authorize the Telegram client. Simply type the code you receive from Telegram in the terminal.

2. **View the data:**

   `fetch_group.py` will save the messages in `data/messages.db`.

   `collect_data.py` will save the statistics in the following files:
      - `data/global_stats.json`,
      - `data/user_stats.json`,
      - and `data/user_stats.db`.

   `get_all_words.py`: the words will be saved in:
      - `data/all_words_case_sensitive_freq.json`, 
      - `data/all_words_case_sensitive_alpha.json`,
      - `data/all_words_case_insensitive_freq.json`,
      - and `data/all_words_case_insensitive_alpha.json`.

## Visualizing The Data (experimental)
- The data you obtained can be used to generate to nice word clouds, check [wordclouds.md](wordcloud-extension/wordclouds.md)
- To create activity graphs and animations using the data you obtained, check [graphs.md](graph-extension/graphs.md)

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
