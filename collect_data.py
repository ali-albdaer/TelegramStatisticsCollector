import os
import json
import logging
import asyncio
import re
import sqlite3
import time
from datetime import datetime
from collections import Counter, defaultdict
from res.config import *
from res.phrases import category_sets, ignored_words
from fetch_group import get_messages


if CONVERT_UNICODE:
    try:
        from unidecode import unidecode
    except ImportError:
        print('Please install the unidecode module to use the CONVERT_UNICODE option.\nRun: pip install unidecode')
        exit(1)


if ANALYZE_SENTIMENTS:
    """
    This is an exmple sentinment analysis pipeline using the transformers library. It may not be accurate depending on the dataset.
    """
    try:
        logging.info('Loading the sentiment analysis pipeline...')
        from transformers import pipeline
        emotion_pipeline = pipeline(*SENTIMENT_PIPELINE_ARGS, **SENTIMENT_PIPELINE_KWARGS)
        logging.info('Sentiment analysis pipeline loaded.')
    except ImportError:
        print('Please install the transformers module to use the ANALYZE_SENTIMENTS option.\nAdditionally, one of torch or tensorflow is required.\nRun: pip install transformers')
        exit(1)


logging.basicConfig(level=logging.INFO)


if not os.path.exists(output_folder):
    os.makedirs(output_folder)


if GET_CHANNEL_LOG:
    with open(log_channel_file, 'w', encoding='utf-8') as file:
        file.write('')


class User:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.name = None
        self.message_count = 0
        self.word_count = 0
        self.letter_count = 0
        self.media_count = 0
        self.reactions_given_count = 0
        self.reactions_received_count = 0
        self.loud_word_count = 0
        self.loud_message_count = 0
        self.curse_count = 0
        self.messages_per_active_day = 0
        self.messages_per_day = 0
        self.words_per_message = 0
        self.media_per_message = 0
        self.rg_ratio = 0
        self.rr_ratio = 0
        self.loudness = 0
        self.naughtiness = 0
        self.messages_by_feeling = Counter()
        self.feeling_ratios = Counter()
        self.word_counter = Counter()  # All words used by the user.
        self.daily_message_counter = Counter()  # Number of messages sent per day.
        self.category_words = defaultdict(Counter)  # Keywords and phrases.
        self.reactions_given = Counter()
        self.reactions_received = Counter()
        self.total_string = ''  # All messages concatenated.
    
    def is_outlier(self):
        below_min = self.message_count < OUTLIER_MIN_MESSAGES or len(self.daily_message_counter) < OUTLIER_MIN_ACTIVE_DAYS
        above_max = self.message_count > OUTLIER_MAX_MESSAGES or len(self.daily_message_counter) > OUTLIER_MAX_ACTIVE_DAYS

        return below_min or above_max


def calculate_user_ratios(user: User, global_stats: dict):
    user.reactions_given_count = sum(user.reactions_given.values())
    user.reactions_received_count = sum(user.reactions_received.values())
    user.messages_per_active_day = user.message_count / len(user.daily_message_counter) if len(user.daily_message_counter) else 0 
    
    default_date = Counter({DEFAULT_DATE: 1})
    delta = datetime.strptime(max(user.daily_message_counter.keys() or default_date), '%Y-%m-%d') - datetime.strptime(min(user.daily_message_counter.keys() or default_date), '%Y-%m-%d')
    user.messages_per_day = user.message_count / delta.days if delta.days else 0

    mc = user.message_count
    user.words_per_message = user.word_count / mc if mc else 0
    user.media_per_message = user.media_count / mc if mc else 0
    user.rg_ratio = user.reactions_given_count / mc if mc else 0
    user.rr_ratio = user.reactions_received_count / mc if mc else 0
    user.loudness = user.loud_word_count / mc if mc else 0
    user.naughtiness = user.curse_count / mc if mc else 0

    if TRIM_OUTLIERS and user.is_outlier():
        return

    if user.messages_per_active_day:
        global_stats['active_users'][user.user_id] = user

    if user.media_per_message:
        global_stats['media_users'][user.user_id] = user

    if user.rg_ratio:
        global_stats['reacting_users'][user.user_id] = user

    if user.rr_ratio:
        global_stats['reacted_users'][user.user_id] = user

    if user.loudness:
        global_stats['loud_users'][user.user_id] = user

    if user.naughtiness:
        global_stats['cursing_users'][user.user_id] = user


def calculate_global_ratios(global_stats: dict):
    gmc = global_stats['message_count']
    delta = datetime.strptime(max(global_stats['daily_message_counter'].keys()), '%Y-%m-%d') - datetime.strptime(min(global_stats['daily_message_counter'].keys()), '%Y-%m-%d')

    global_stats['ratios']['messages_per_active_day'] = gmc / len(global_stats['daily_message_counter']) if len(global_stats['daily_message_counter']) else 0
    global_stats['ratios']['messages_per_day'] = gmc / delta.days if delta.days else 0
    global_stats['ratios']['words_per_message'] = global_stats['word_count'] / gmc
    global_stats['ratios']['media_per_message'] = global_stats['media_count'] / gmc
    global_stats['ratios']['reaction_ratio'] = global_stats['reaction_count'] / gmc
    global_stats['ratios']['loudness'] = global_stats['loud_word_count'] / gmc
    global_stats['ratios']['naughtiness'] = global_stats['curse_count'] / gmc


def analyze_message(user: User, global_stats: dict):
    text = user.total_string

    for category, elements in category_sets.items():
        for element in elements:
            if isinstance(element, tuple):
                primary_key = element[0]
                aliases = element[1:]

            else:
                primary_key = element
                aliases = ()

            if PLURALIZE_CATEGORIES:
                aliases += tuple(alias + 's' if not alias.endswith('s') else alias[:-1]+'ies' for alias in aliases)
                aliases += (primary_key + 's' if not primary_key.endswith('s') else primary_key[:-1]+'ies',)

                if primary_key.endswith('y'):
                    aliases += (primary_key[:-1] + 'ies',)

                elif not primary_key.endswith('s'):
                    aliases += (primary_key + 's',)
            
            pattern = r'\b(?:{})\b'.format('|'.join([re.escape(alias) for alias in (primary_key,) + aliases]))
            count = len(re.findall(pattern, text))
            
            if count > 0:
                if isinstance(element, tuple):
                    primary_key = element[0]

                else:
                    primary_key = element
                    
                global_stats['top_categories'][category][primary_key] += count
                user.category_words[category][primary_key] += count

                if category == 'curses':
                    user.curse_count += count
                    global_stats['curse_count'] += count


def analyze_sentiments(text: str):
    chunk_size = 512

    if len(text) <= chunk_size:
        results = emotion_pipeline(text)[0]
        result = {}
        
        for sentiment in results:
            result.update({sentiment['label']: sentiment['score']})

    else:
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        chunk_count = len(chunks)
        result = {}

        for chunk in chunks:
            results = emotion_pipeline(chunk)[0]

            for sentiment in results:
                label = sentiment['label']
                score = sentiment['score']

                result[label] = result.get(label, 0) + score / chunk_count

    return result


def fetch_message_stats(message, user_stats: dict, global_stats: dict):
    sender_id = message.sender_id
    user = user_stats[sender_id]
    user.message_count += 1

    if not user.name:
        if message.sender:
            if message.sender.first_name:
                user.name = message.sender.first_name + (' ' + message.sender.last_name if message.sender.last_name else '')
            elif message.sender.username:
                user.name = message.sender.username
            else:
                user.name = 'Unknown User'
        else:
            user.name = 'Unknown User'

    date_str = message.date.strftime('%Y-%m-%d')
    user.daily_message_counter[date_str] += 1

    if message.media:
        user.media_count += 1
        global_stats['media_count'] += 1

    if COUNT_REACTIONS and message.reactions:
        for reaction in message.reactions:
            if reaction.peer_id:
                reaction_user = user_stats.get(reaction.peer_id.user_id, None)

                if not reaction_user:
                    reaction_user = User(reaction.peer_id.user_id)
                    user_stats[reaction.peer_id.user_id] = reaction_user

                reaction_user.reactions_given[reaction.reaction] += 1

            user.reactions_received[reaction.reaction] += 1
            global_stats['top_reactions'][reaction.reaction] += 1
            global_stats['reaction_count'] += 1

    if not message.text:
        return
    
    if CONVERT_UNICODE:
        text = unidecode(message.text)

    else:
        text = message.text.encode('utf-8', errors='replace').decode('utf-8')

    if GET_CHANNEL_LOG:
        if SHOW_DATE:
            date_str = message.date.strftime('%Y-%m-%d %H:%M:%S')
            _text = f'[ {date_str} ] <{user.name}> {text}\n'

        else:
            _text = f'<{user.name}> {text}\n'

        with open(log_channel_file, 'a', encoding='utf-8') as file:
            file.write(_text)

    if IGNORE_URLS:
        text = re.sub(r'http\S+', ' ', text)

    if REMOVE_ACCENTS:
        for letter, accents in ACCENTED_CHARS.items():
            text = re.sub(f'[{accents}]', letter, text)

    # Pattern for matching mentions, [name](tg://user?id=id)
    pattern = r'\[(.*?)\]\(tg://user\?id=(\d+)\)'
    match = re.search(pattern, text)

    if match:
        name = match.group(1)
        text = re.sub(pattern, name, text)

    if ANALYZE_SENTIMENTS:
        try:
            sentiments = analyze_sentiments(text)

        except Exception as e:
            logging.error(f'Error in sentiment analysis: {e}')
            sentiments = {}

        user.feeling_ratios.update(sentiments)
        global_stats['feeling_ratios'].update(sentiments)
        
        filtered_sentiments = {k: v for k, v in sentiments.items() if dominant_sentiment_filter(k, v)}
        dominant_sentiment = max(filtered_sentiments, key=filtered_sentiments.get) if filtered_sentiments else None
        if dominant_sentiment:
            user.messages_by_feeling[dominant_sentiment] += 1
            global_stats['messages_by_feeling'][dominant_sentiment] += 1

    if text.isupper():
        user.loud_message_count += 1
        global_stats['loud_message_count'] += 1

    words = [word for word in re.findall(r'\b\w+\b', text) if len(word) >= MIN_WORD_LENGTH]
    word_count = len(words)
    letter_count = sum(len(word) for word in words)

    loud_words = [word for word in words if word.isupper()]
    user.loud_word_count += len(loud_words)
    global_stats['loud_word_count'] += len(loud_words)

    if CASE_INSENSITIVE:
        text = text.lower()
        words = [word.lower() for word in words]

    if IGNORE_COMMON_WORDS:
        words = [word for word in words if word not in ignored_words]

    user.word_counter.update(words)
    user.word_count += word_count
    user.letter_count += letter_count

    global_stats['top_words'].update(words)
    global_stats['word_count'] += word_count
    global_stats['letter_count'] += letter_count

    # Update the total string for category matching along with a separator. 
    # Part of the string analysis is done cumulatively in the analyze_message function.
    user.total_string += text + '\n\n\n'


async def collect_stats():
    user_stats = {}
    global_stats = {
        'id': telegram_group_id,
        'name': telegram_group_name,
        'message_count': 0,
        'word_count': 0,
        'letter_count': 0,
        'media_count': 0,
        'reaction_count': 0,
        'loud_word_count': 0,
        'loud_message_count': 0,
        'curse_count': 0,
        'ratios': {
            'messages_per_active_day': 0,
            'messages_per_day': 0,
            'words_per_message': 0,
            'media_per_message': 0,
            'reaction_ratio': 0,
            'loudness': 0,
            'naughtiness': 0,
        },
        'messages_by_feeling': Counter(),
        'feeling_ratios': Counter(),
        'daily_message_counter': Counter(),
        'active_users': dict(),
        'media_users': dict(),
        'loud_users': dict(),
        'reacting_users': dict(),
        'reacted_users': dict(),
        'cursing_users': dict(),
        'top_reactions': Counter(),
        'top_categories': defaultdict(Counter),
        'top_words': Counter(),
    }

    processed_messages = 0
    total_messages = sum(1 for _ in get_messages())

    for message in get_messages():
        if message.sender_id:
            if message.sender_id not in user_stats:
                user_stats[message.sender_id] = User(message.sender_id)

            fetch_message_stats(message, user_stats, global_stats)

        processed_messages += 1
        if SHOW_PROGRESS_BAR:
            print(f'\rProcessed Messages: [{processed_messages} / {total_messages}]', end='')

    if SHOW_PROGRESS_BAR:
        print()

    total_users = len(user_stats)
    if not total_users:
        print('No data was collected. Exiting...')
        exit(0)

    for i, user in enumerate(user_stats.values(), 1):
        analyze_message(user, global_stats)

        if CALCULATE_USER_RATIOS:
            calculate_user_ratios(user, global_stats)

        global_stats['daily_message_counter'].update(user.daily_message_counter)
        global_stats['message_count'] += user.message_count

        if SHOW_PROGRESS_BAR:
            print(f'\rProcessed Users: [{i} / {len(user_stats)}]', end='')

    if SHOW_PROGRESS_BAR:
        print()

    if not global_stats['message_count']:
        print("No messages to analyze. Exiting...")
        exit(0)

    if CALCULATE_GLOBAL_RATIOS:
        calculate_global_ratios(global_stats)

    save_global_stats(global_stats)
    save_user_stats(user_stats)


def save_global_stats(global_stats: dict):
    limited_top_active_users = sorted(global_stats['active_users'].items(), key=lambda x: x[1].messages_per_active_day if GLOBAL_RANKING_BY_RATIO else x[1].message_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_media_users = sorted(global_stats['media_users'].items(), key=lambda x: x[1].media_per_message if GLOBAL_RANKING_BY_RATIO else x[1].media_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_reacted_users = sorted(global_stats['reacted_users'].items(), key=lambda x: x[1].rr_ratio if GLOBAL_RANKING_BY_RATIO else x[1].reactions_received_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_reacting_users = sorted(global_stats['reacting_users'].items(), key=lambda x: x[1].rg_ratio if GLOBAL_RANKING_BY_RATIO else x[1].reactions_given_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_loud_users = sorted(global_stats['loud_users'].items(), key=lambda x: x[1].loudness if GLOBAL_RANKING_BY_RATIO else x[1].loud_word_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_cursing_users = sorted(global_stats['cursing_users'].items(), key=lambda x: x[1].naughtiness if GLOBAL_RANKING_BY_RATIO else x[1].curse_count, reverse=True)[:GLOBAL_RANKING_LIMIT]

    json_global_stats = {
        'id': global_stats['id'],
        'name': global_stats['name'],
        'message_count': global_stats['message_count'],
        'word_count': global_stats['word_count'],
        'letter_count': global_stats['letter_count'],
        'media_count': global_stats['media_count'],
        'reaction_count': global_stats['reaction_count'],
        'loud_word_count': global_stats['loud_word_count'],
        'loud_message_count': global_stats['loud_message_count'],
        'curse_count': global_stats['curse_count'],
        **({'ratios': global_stats['ratios']} if CALCULATE_GLOBAL_RATIOS else {}),
        **({'messages_by_feeling': dict(global_stats['messages_by_feeling'])} if ANALYZE_SENTIMENTS else {}),
        **({'feeling_ratios': dict(global_stats['feeling_ratios'])} if ANALYZE_SENTIMENTS else {}),
        'top_reactions': dict(global_stats['top_reactions'].most_common(GLOBAL_REACTION_LIMIT)),
        'top_active_days': dict(global_stats['daily_message_counter'].most_common(GLOBAL_ACTIVE_DAYS_LIMIT)),
        'top_active_users': {user_id: {'name': user.name, 'messages_per_active_day': user.messages_per_active_day, 'message_count': user.message_count, 'word_count': user.word_count, 'letter_count': user.letter_count} for user_id, user in limited_top_active_users},
        'top_loud_users': {user_id: {'name': user.name, 'loudness': user.loudness, 'loud_word_count': user.loud_word_count} for user_id, user in limited_top_loud_users},
        'top_media_users': {user_id: {'name': user.name, 'media_per_message': user.media_per_message, 'media_count': user.media_count} for user_id, user in limited_top_media_users},
        'top_reacted_users': {user_id: {'name': user.name, 'rr_ratio': user.rr_ratio, 'reactions_received_count': user.reactions_received_count} for user_id, user in limited_top_reacted_users},
        'top_reacting_users': {user_id: {'name': user.name, 'rg_ratio': user.rg_ratio, 'reactions_given_count': user.reactions_given_count} for user_id, user in limited_top_reacting_users},
        'top_cursing_users': {user_id: {'name': user.name, 'naughtiness': user.naughtiness, 'curse_count': user.curse_count} for user_id, user in limited_top_cursing_users},
        'top_categories': {k: dict(v.most_common(GLOBAL_CATEGORY_LIMIT)) for k, v in global_stats['top_categories'].items()},
        'top_words': dict(global_stats['top_words'].most_common(GLOBAL_WORD_LIMIT)),
    }

    with open(global_stats_json, 'w', encoding='utf-8') as file:
        json.dump(json_global_stats, file, indent=4, ensure_ascii=False)


def save_user_stats(user_stats: dict[int, User]):
    with open(user_stats_json, 'w', encoding='utf-8') as file:
        limited_user_stats = {
            user_id: {
                'id': user.user_id,
                'name': user.name,
                'message_count': user.message_count,
                'word_count': user.word_count,
                'letter_count': user.letter_count,
                'media_count': user.media_count,
                'reactions_given_count': user.reactions_given_count,
                'reactions_received_count': user.reactions_received_count,
                'loud_word_count': user.loud_word_count,
                'loud_message_count': user.loud_message_count,
                'curse_count': user.curse_count,
                **({'ratios': {
                    'messages_per_active_day': user.messages_per_active_day,
                    'messages_per_day': user.messages_per_day,
                    'words_per_message': user.words_per_message,
                    'media_per_message': user.media_per_message,
                    'rg_ratio': user.rg_ratio,
                    'rr_ratio': user.rr_ratio,
                    'loudness': user.loudness,
                    'naughtiness': user.naughtiness,
                }} if CALCULATE_USER_RATIOS else {}),
                **({'messages_by_feeling': dict(user.messages_by_feeling)} if ANALYZE_SENTIMENTS else {}),
                **({'feeling_ratios': dict(user.feeling_ratios)} if ANALYZE_SENTIMENTS else {}),
                'top_reactions_given': dict(user.reactions_given.most_common(USER_REACTION_LIMIT)),
                'top_reactions_received': dict(user.reactions_received.most_common(USER_REACTION_LIMIT)),
                'top_active_days': dict(user.daily_message_counter.most_common(USER_ACTIVE_DAYS_LIMIT)),
                'top_categories': {k: dict(v.most_common(USER_CATEGORY_LIMIT)) for k, v in user.category_words.items()},
                'top_words': dict(user.word_counter.most_common(USER_WORD_LIMIT))
            }
            for user_id, user in user_stats.items()
        }
        json.dump(limited_user_stats, file, indent=4, ensure_ascii=False)

    conn = sqlite3.connect(user_stats_db)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            message_count INTEGER,
            word_count INTEGER,
            letter_count INTEGER,
            media_count INTEGER,
            reactions_given_count INTEGER,
            reactions_received_count INTEGER,
            loud_word_count INTEGER,
            loud_message_count INTEGER,
            curse_count INTEGER,
            messages_per_active_day REAL,
            messages_per_day REAL,
            words_per_message REAL,
            media_per_message REAL,
            rg_ratio REAL,
            rr_ratio REAL,
            loudness REAL,
            naughtiness REAL,
            messages_by_feeling TEXT,
            feelings_ratios TEXT,
            top_reactions_given TEXT,
            top_reactions_received TEXT,
            top_active_days TEXT,
            top_categories TEXT,
            top_words TEXT
        )
    ''')

    for user_id, user in user_stats.items():
        cursor.execute('''
            INSERT OR REPLACE INTO user_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, user.name, 
            user.message_count, user.word_count, user.letter_count, user.media_count, 
            user.reactions_given_count, user.reactions_received_count, 
            user.loud_word_count, user.loud_message_count,
            user.curse_count,
            user.messages_per_active_day,
            user.messages_per_day, user.words_per_message, user.media_per_message, 
            user.rg_ratio, user.rr_ratio,
            user.loudness, user.naughtiness,
            json.dumps(dict(user.messages_by_feeling)),
            json.dumps(dict(user.feeling_ratios)),
            json.dumps(dict(user.reactions_given.most_common(USER_REACTION_LIMIT))),
            json.dumps(dict(user.reactions_received.most_common(USER_REACTION_LIMIT))),
            json.dumps(dict(user.daily_message_counter.most_common(USER_ACTIVE_DAYS_LIMIT))),
            json.dumps({k: dict(v.most_common(USER_CATEGORY_LIMIT)) for k, v in user.category_words.items()}),
            json.dumps(dict(user.word_counter.most_common(USER_WORD_LIMIT))),
        ))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    start = time.time()

    try:
        asyncio.run(collect_stats())

    except KeyboardInterrupt:
        print('\n[ Program Interrupted. ]')

    else:
        print('[ Data Collection Completed. ]')

    end = time.time()
    print(f'Execution Time: {end - start:.2f} seconds')
