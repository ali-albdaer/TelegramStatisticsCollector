"""
Configuration file for the Telegram Statistics Collector.

Create a `config.py` file in this directory or change the name of this file to `config.py` and fill in the required fields. 

- The first set of variables are for the Telegram API configuration, which are required for the script to work. 
- The second set contains flags that can be toggled to change the behavior of the script. 
- The third set contains limits for the number of words, reactions, categories, etc., that are stored in the db and json files.
- The fourth set contains sentiment analysis configuration.
- The fifth set contains file paths for the data files generated by the script.
"""


# Telegram Configuration
development = False

if development:
    telegram_group_id = -1234567890  # Example Telegram group ID, can be obtained using a bot like @getidsbot
    output_folder = 'data_dev'

else:
    telegram_group_id = -1234567891  #    ^
    output_folder = 'data'

telegram_user = 'example_username'
telegram_phone = '+1234567890'
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
CALCULATE_USER_RATIOS = True  # Set to True to calculate the ratio of words/reactions/categories to the total count of messages.
CALCULATE_GLOBAL_RATIOS = True  # Same as above, but for global statistics.
GLOBAL_RANKING_BY_RATIO = False  # Set to False to rank users by total count instead of ratio. Applies to all categories. (e.g., active days, media count, etc.)
TRIM_OUTLIERS = False  # Set to True to trim users with messages/active days out of the bounds below. Currently only affects the global rankings.


# Limits
MIN_WORD_LENGTH = 1  # Minimum length for a string to be considered a word

USER_WORD_LIMIT = 1000  # Limit for top words stored per user
USER_REACTION_LIMIT = 100  # Limit for top reactions stored per user
USER_CATEGORY_LIMIT = 1000  # Limit for top categories stored per user
USER_ACTIVE_DAYS_LIMIT = 365  # Limit for top active days stored per user

GLOBAL_WORD_LIMIT = 10000  # Limit for top global words.
GLOBAL_REACTION_LIMIT = 100  # Limit for top global reactions.
GLOBAL_CATEGORY_LIMIT = 1000  # Limit for top category mentions (see phrases.py)
GLOBAL_RANKING_LIMIT = 100  # Limit for global ranking data (e.g., top users by active days, by media count, etc.)
GLOBAL_ACTIVE_DAYS_LIMIT = 365  # Limit for top global active days.

OUTLIER_MIN_MESSAGES = 0
OUTLIER_MAX_MESSAGES = 10**5
OUTLIER_MIN_ACTIVE_DAYS = 0
OUTLIER_MAX_ACTIVE_DAYS = 365*10


# Sentiment Analysis [EXPERIMENTAL]: Requires the `transformers` library, along with the `torch` or `tensorflow`.
# If enabled, the program will take a significantally longer time to run.
# Example output: 
"""
{
    "0123456789": {
        ...,
        "feelings": {
            "sadness": [
                7,  // Number of messages with 'sadness' as the dominant sentiment.
                11.464838723652065  // The sum of 'saddness' scores across all messages sent by the user.
            ],
            "neutral": [
                154,
                127.76049086579587
            ],
            "surprise": [
                7,
                15.356227628421038
            ],
            "anger": [
                4,
                6.874813125003129
            ],
            "disgust": [
                7,
                9.78928733302746
            ],
            "joy": [
                7,
                11.871904620085843
            ],
            "fear": [
                3,
                5.882437665830366
            ]
        },
    },
    ...
}
"""

ANALYZE_SENTIMENTS = False
SENTIMENT_PIPELINE_ARGS = ('text-classification', )
SENTIMENT_PIPELINE_KWARGS = {
    'model': 'j-hartmann/emotion-english-distilroberta-base',
    'top_k': 2,
}
# Example filter for the dominant sentiment. If the score is less than 0.30, that message will not be classified as having a dominant sentiment.
# The overall ratio calculation is not affected by this filter.
dominant_sentiment_filter = lambda label, score: score >= 0.30


# File paths for collect_data.py
session_file = f'{telegram_user}.session'
log_channel_file = f'{output_folder}/channel_log.txt'
global_stats_json = f'{output_folder}/global_stats.json'
user_stats_json = f'{output_folder}/user_stats.json'
user_stats_db = f'{output_folder}/users.db'


# File paths for get_all_words.py
sensitive_freq_json = f'{output_folder}/all_words_case_sensitive_freq.json'
sensitive_alpha_json = f'{output_folder}/all_words_case_sensitive_alpha.json'
insensitive_freq_json = f'{output_folder}/all_words_case_insensitive_freq.json'
insensitive_alpha_json = f'{output_folder}/all_words_case_insensitive_alpha.json'


# Others
DEFAULT_DATE = '2024-01-01'  # Default date for the first message sent by users. (used instead of an empty date)
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
