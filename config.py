# Telegram Configuration
telegram_user = 'example_username'
telegram_phone = '+1234567890'
telegram_group_id = -1234567890  # Example Telegram group ID, can be obtained using a bot like @getidsbot
api_id = '12345678'  # Example Telegram API ID, can be obtained from https://my.telegram.org
api_hash = 'example_api_hash'  # Example Telegram API Hash, also obtained from https://my.telegram.org


# Flags
IGNORE_COMMON_WORDS = False
SHOW_PROGRESS_BAR = True
CASE_INSENSITIVE = True
CONVERT_UNICODE = True  # Set to False to keep unicode characters in the output. (not recommended)
LOGOUT = False  # Set to True to delete the current session file.


# Limits
TOP_MESSAGE_LIMIT = 20  # Limit for top messages stored per user
TOP_ACTIVE_DAYS_LIMIT = 10  # Limit for top active days stored per user
GLOBAL_MESSAGE_LIMIT = 20  # Limit for top global messages
GLOBAL_RANKING_LIMIT = 20  # Limit for global ranking data (e.g., loud_users, cursing_users)
CATEGORY_MENTION_LIMIT = 10**3  # Limit for category mentions (lookup.py)


# File Paths
session_file = f'data/{telegram_user}.session'
global_stats_json = 'data/global_stats.json'
user_stats_json = 'data/user_stats.json'
user_stats_db = 'data/users.db'


# File paths for words.py
sensitive_freq_json = 'data/all_words_case_sensitive_freq.json'
sensitive_alpha_json = 'data/all_words_case_sensitive_alpha.json'
insensitive_freq_json = 'data/all_words_case_insensitive_freq.json'
insensitive_alpha_json = 'data/all_words_case_insensitive_alpha.json'

# test 2
