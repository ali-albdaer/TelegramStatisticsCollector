"""
Configuration file for the Telegram Statistics Collector.

Create a `config.py` file in this directory or change the name of this file to `config.py` and fill in the required fields. 

- The first set of variables are for the Telegram API configuration, which are required for the script to work. 
- The second set contains flags that can be toggled to change the behavior of the script. 
- The third set contains limits for the number of items stored in the database and json files.
- The last set contains file paths for the data files used by the script.
"""


# Telegram Configuration
telegram_user = 'example_username'
telegram_phone = '+1234567890'
telegram_group_id = -1234567890  # Example Telegram group ID, can be obtained using a bot like @getidsbot
api_id = '12345678'  # Example Telegram API ID, can be obtained from https://my.telegram.org
api_hash = 'example_api_hash'  # Example Telegram API Hash, also obtained from https://my.telegram.org


# Flags
CASE_INSENSITIVE = True
CONVERT_UNICODE = False  # Set to True to convert unicode characters to their ASCII equivalent.
REMOVE_ACCENTS = False  # Set to True to remove accents from characters.
PLURALIZE_CATEGORIES = False  # Set to True to count plural forms of categories as the same word.
IGNORE_COMMON_WORDS = False  # Set to True to ignore the words found in res/phrases.py.
IGNORE_URLS = False  # Replaces URLs with a white space ' '.
GET_CHANNEL_LOG = True  # Set to True to get the log of the chat as a text file.
SHOW_DATE = False  # Set to True to show the date of the messages in the log file.
SHOW_PROGRESS_BAR = True
COUNT_REACTIONS = True
LOGOUT = False  # Set to True to delete the session file after running the script, you would need to authenticate Telegram again.
GLOBAL_RANKING_BY_RATIO = True  # Set to False to rank users by total count instead of ratio. Applies to all categories. (e.g., active days, media count, etc.)

ACCENTED_CHARS = {
    "a": "áàâäãåā",
    "c": "çćč",
    "e": "éèêëēę",
    "i": "íìîïī",
    "g": "ğ",
    "n": "ñń",
    "o": "óòôöõ",
    "u": "úùûü",
    "y": "ýÿ",
    "A": "ÁÀÂÄÃÅ",
    "C": "ÇĆČ",
    "E": "ÉÈÊË",
    "I": "ÍÌÎÏ",
    "G": "Ğ",
    "N": "ÑŃ",
    "O": "ÓÒÔÖÕ",
    "U": "ÚÙÛÜ",
    "Y": "ÝŸ"
}


# Limits
MIN_WORD_LENGTH = 1  # Minimum length for a string to be considered a word

USER_WORD_LIMIT = 50  # Limit for top words stored per user
USER_REACTION_LIMIT = 20  # Limit for top reactions stored per user
USER_CATEGORY_LIMIT = 1000  # Limit for top categories stored per user
USER_ACTIVE_DAYS_LIMIT = 30  # Limit for top active days stored per user

GLOBAL_WORD_LIMIT = 100  # Limit for top global words.
GLOBAL_REACTION_LIMIT = 20  # Limit for top global reactions.
GLOBAL_CATEGORY_LIMIT = 1000  # Limit for top category mentions (see phrases.py)
GLOBAL_RANKING_LIMIT = 50  # Limit for global ranking data (e.g., top users by active days, by media count, etc.)


# File paths for collect_data.py
session_file = f'data/{telegram_user}.session'
log_channel_file = 'data/channel_log.txt'
global_stats_json = 'data/global_stats.json'
user_stats_json = 'data/user_stats.json'
user_stats_db = 'data/users.db'


# File paths for get_all_words.py
sensitive_freq_json = 'data/all_words_case_sensitive_freq.json'
sensitive_alpha_json = 'data/all_words_case_sensitive_alpha.json'
insensitive_freq_json = 'data/all_words_case_insensitive_freq.json'
insensitive_alpha_json = 'data/all_words_case_insensitive_alpha.json'
