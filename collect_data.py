import os
import json
import logging
import asyncio
import re
import sqlite3
from collections import Counter, defaultdict
from telethon import TelegramClient

# Create the following files in the res directory or rename the examples in res.
from res.config import * 
from res.phrases import category_sets, ignored_words


if CONVERT_UNICODE:
    try:
        from unidecode import unidecode
    except ImportError:
        print('Please install the unidecode module to use the CONVERT_UNICODE option.\nRun: pip install unidecode')
        exit(1)


logging.basicConfig(level=logging.INFO)


if not os.path.exists(output_folder):
    os.makedirs(output_folder)


if GET_CHANNEL_LOG:
    with open(log_channel_file, 'w', encoding='utf-8') as file:
        file.write('')


telegram_client = TelegramClient(session_file, api_id, api_hash)


class User:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.name = None
        self.message_count = 0
        self.word_count = 0
        self.letter_count = 0
        self.media_count = 0
        self.loud_message_count = 0  # Number of messages in all caps.
        self.curse_count = 0  # Number of curse words used by the user.
        self.reactions_given_count = 0
        self.reactions_received_count = 0
        self.word_counter = Counter()  # All words used by the user.
        self.daily_message_counter = Counter()  # Number of messages sent per day.
        self.category_words = defaultdict(Counter)  # Keywords and phrases.
        self.reactions_given = Counter()
        self.reactions_received = Counter()
        self.total_string = ''  # All messages concatenated.

    def calculate_ratios(self):
        self.reactions_given_count = sum(self.reactions_given.values())
        self.reactions_received_count = sum(self.reactions_received.values())

        self.activeness = self.message_count / USER_ACTIVE_DAYS_LIMIT if USER_ACTIVE_DAYS_LIMIT else 0
        self.media_ratio = (self.media_count * 100) / self.message_count if self.message_count else 0
        self.rg_ratio = (self.reactions_given_count * 100) / self.message_count if self.message_count else 0
        self.rr_ratio = (self.reactions_received_count * 100) / self.message_count if self.message_count else 0
        self.loudness = (self.loud_message_count * 100) / self.message_count if self.message_count else 0
        self.naughtiness = (self.curse_count * 100) / self.message_count if self.message_count else 0

        return self.message_count, self.activeness, self.media_ratio, self.rg_ratio, self.rr_ratio, self.loudness, self.naughtiness


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

    # Collect reactions.
    if COUNT_REACTIONS and message.reactions and message.reactions.recent_reactions:
        for reaction in message.reactions.recent_reactions:
            if reaction.peer_id:
                reaction_user = user_stats.get(reaction.peer_id.user_id, None)

                if not reaction_user:
                    reaction_user = User(reaction.peer_id.user_id)
                    user_stats[reaction.peer_id.user_id] = reaction_user

                reaction_user.reactions_given[reaction.reaction.emoticon] += 1

            user.reactions_received[reaction.reaction.emoticon] += 1
            global_stats['top_reactions'][reaction.reaction.emoticon] += 1
            global_stats['reaction_count'] += 1

    if not message.text:
        return
    
    if CONVERT_UNICODE:
        text = unidecode(message.text)

    else:
        text = message.text.encode('utf-8', errors='replace').decode('utf-8')

    if text.isupper():
        user.loud_message_count += 1
        global_stats['loud_message_count'] += 1

    if GET_CHANNEL_LOG: # Logging is done before processing the text.
        if SHOW_DATE:
            date_str = message.date.strftime('%Y-%m-%d %H:%M:%S')
            _text = f'[ {date_str} ] <{user.name}> {text}\n'

        else:
            _text = f'<{user.name}> {text}\n'

        with open(log_channel_file, 'a', encoding='utf-8') as file:
            file.write(_text)

    if CASE_INSENSITIVE:
        text = text.lower()

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

    words = [word for word in re.findall(r'\b\w+\b', text) if len(word) >= MIN_WORD_LENGTH]
    word_count = len(words)
    letter_count = sum(len(word) for word in words)

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
    await telegram_client.connect()

    if not await telegram_client.is_user_authorized():
        await telegram_client.send_code_request(telegram_phone)
        await telegram_client.sign_in(telegram_phone, input('Enter the code you received on Telegram: '))

    group_entity = await telegram_client.get_entity(telegram_group_id)
    telegram_group_name = group_entity.title if group_entity.title else 'Unknown Group'

    user_stats = {}
    global_stats = {
        'id': telegram_group_id,
        'name': telegram_group_name,
        'message_count': 0,
        'word_count': 0,
        'letter_count': 0,
        'media_count': 0,
        'loud_message_count': 0,
        'curse_count': 0,
        'reaction_count': 0,
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

    total_messages = (await telegram_client.get_messages(group_entity, limit=0)).total
    processed_messages = 0

    async for message in telegram_client.iter_messages(group_entity):
        if message.sender_id:  # Skip system messages.
            if message.sender_id not in user_stats:
                user_stats[message.sender_id] = User(message.sender_id)

            fetch_message_stats(message, user_stats, global_stats)

        processed_messages += 1
        if SHOW_PROGRESS_BAR:
            print(f'\rProcessed Messages: [{processed_messages} / {total_messages}]', end='')

    if SHOW_PROGRESS_BAR:
        print()

    for user in user_stats.values():
        analyze_message(user, global_stats)

        message_count, activeness, media_ratio, rg_ratio, rr_ratio, loudness, naughtiness = user.calculate_ratios()
        global_stats['message_count'] += message_count

        if activeness:
            global_stats['active_users'][user.user_id] = user

        if media_ratio:
            global_stats['media_users'][user.user_id] = user

        if rg_ratio:
            global_stats['reacting_users'][user.user_id] = user

        if rr_ratio:
            global_stats['reacted_users'][user.user_id] = user

        if loudness:
            global_stats['loud_users'][user.user_id] = user

        if naughtiness:
            global_stats['cursing_users'][user.user_id] = user

        global_stats['daily_message_counter'].update(user.daily_message_counter)

        if SHOW_PROGRESS_BAR:
            print(f'\rProcessed Users: [{len(global_stats["active_users"])} / {len(user_stats)}]', end='')

    if SHOW_PROGRESS_BAR:
        print()

    save_global_stats(global_stats)
    save_user_stats(user_stats)

    await telegram_client.disconnect()

    if LOGOUT:
        os.remove(session_file)

    print('[ Program Finished. ]')


def save_global_stats(global_stats: dict):
    global_stats['top_active_days'] = dict(global_stats['daily_message_counter'].most_common(GLOBAL_ACTIVE_DAYS_LIMIT))
    global_stats['activeness'] = global_stats['message_count'] / GLOBAL_ACTIVE_DAYS_LIMIT if GLOBAL_ACTIVE_DAYS_LIMIT else 0
    global_stats['media_ratio'] = (global_stats['media_count'] * 100) / global_stats['message_count'] if global_stats['message_count'] else 0
    global_stats['reaction_ratio'] = (global_stats['reaction_count'] * 100) / global_stats['message_count'] if global_stats['message_count'] else 0
    global_stats['loudness'] = (global_stats['loud_message_count'] * 100) / global_stats['message_count'] if global_stats['message_count'] else 0
    global_stats['naughtiness'] = (global_stats['curse_count'] * 100) / global_stats['message_count'] if global_stats['message_count'] else 0

    limited_top_active_users = sorted(global_stats['active_users'].items(), key=lambda x: x[1].activeness if GLOBAL_RANKING_BY_RATIO else x[1].message_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_media_users = sorted(global_stats['media_users'].items(), key=lambda x: x[1].media_ratio if GLOBAL_RANKING_BY_RATIO else x[1].media_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_reacted_users = sorted(global_stats['reacted_users'].items(), key=lambda x: x[1].rr_ratio if GLOBAL_RANKING_BY_RATIO else x[1].reactions_received_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_reacting_users = sorted(global_stats['reacting_users'].items(), key=lambda x: x[1].rg_ratio if GLOBAL_RANKING_BY_RATIO else x[1].reactions_given_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_loud_users = sorted(global_stats['loud_users'].items(), key=lambda x: x[1].loudness if GLOBAL_RANKING_BY_RATIO else x[1].loud_message_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_cursing_users = sorted(global_stats['cursing_users'].items(), key=lambda x: x[1].naughtiness if GLOBAL_RANKING_BY_RATIO else x[1].curse_count, reverse=True)[:GLOBAL_RANKING_LIMIT]

    json_global_stats = {
        'id': global_stats['id'],
        'name': global_stats['name'],
        'message_count': global_stats['message_count'],
        'word_count': global_stats['word_count'],
        'letter_count': global_stats['letter_count'],
        'media_count': global_stats['media_count'],
        'loud_messages_count': global_stats['loud_message_count'],
        'curse_count': global_stats['curse_count'],
        'reaction_count': global_stats['reaction_count'],
        'activeness': global_stats['activeness'],
        'media_ratio': global_stats['media_ratio'],
        'reaction_ratio': global_stats['reaction_ratio'],
        'loudness': global_stats['loudness'],
        'naughtiness': global_stats['naughtiness'],
        'top_reactions': dict(global_stats['top_reactions'].most_common(GLOBAL_REACTION_LIMIT)),
        'top_active_days': dict(global_stats['top_active_days']),
        'top_active_users': {user_id: {'name': user.name, 'activeness': user.activeness, 'message_count': user.message_count, 'word_count': user.word_count, 'letter_count': user.letter_count} for user_id, user in limited_top_active_users},
        'top_loud_users': {user_id: {'name': user.name, 'loudness': user.loudness, 'loud_message_count': user.loud_message_count} for user_id, user in limited_top_loud_users},
        'top_media_users': {user_id: {'name': user.name, 'media_ratio': user.media_ratio, 'media_count': user.media_count} for user_id, user in limited_top_media_users},
        'top_reacted_users': {user_id: {'name': user.name, 'rr_ratio': user.rr_ratio, 'reactions_received_count': user.reactions_received_count} for user_id, user in limited_top_reacted_users},
        'top_reacting_users': {user_id: {'name': user.name, 'rg_ratio': user.rg_ratio, 'reactions_given_count': user.reactions_given_count} for user_id, user in limited_top_reacting_users},
        'top_cursing_users': {user_id: {'name': user.name, 'naughtiness': user.naughtiness, 'curse_count': user.curse_count} for user_id, user in limited_top_cursing_users},
        'top_categories': {k: dict(v.most_common(GLOBAL_CATEGORY_LIMIT)) for k, v in global_stats['top_categories'].items()},
        'top_words': dict(global_stats['top_words'].most_common(GLOBAL_WORD_LIMIT)),
    }

    with open(global_stats_json, 'w', encoding='utf-8') as file:
        json.dump(json_global_stats, file, indent=4, ensure_ascii=False)


def save_user_stats(user_stats: dict):
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
                'loud_message_count': user.loud_message_count,
                'curse_count': user.curse_count,
                'activeness': user.activeness,
                'media_ratio': user.media_ratio,
                'rg_ratio': user.rg_ratio,
                'rr_ratio': user.rr_ratio,
                'loudness': user.loudness,
                'naughtiness': user.naughtiness,
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
            loud_message_count INTEGER,
            curse_count INTEGER,
            activeness REAL,
            media_ratio REAL,
            rg_ratio REAL,
            rr_ratio REAL,
            loudness REAL,
            naughtiness REAL,
            top_reactions_given TEXT,
            top_reactions_received TEXT,
            top_active_days TEXT,
            top_categories TEXT,
            top_words TEXT
        )
    ''')

    for user_id, user in user_stats.items():
        cursor.execute('''
            INSERT OR REPLACE INTO user_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, user.name, 
            user.message_count, user.word_count, user.letter_count, user.media_count, 
            user.reactions_given_count, user.reactions_received_count, 
            user.loud_message_count, user.curse_count, 
            user.activeness, user.media_ratio, user.rg_ratio, user.rr_ratio,
            user.loudness, user.naughtiness,
            json.dumps(dict(user.reactions_given.most_common(USER_REACTION_LIMIT))),
            json.dumps(dict(user.reactions_received.most_common(USER_REACTION_LIMIT))),
            json.dumps(dict(user.daily_message_counter.most_common(USER_ACTIVE_DAYS_LIMIT))),
            json.dumps({k: dict(v.most_common(USER_CATEGORY_LIMIT)) for k, v in user.category_words.items()}),
            json.dumps(dict(user.word_counter.most_common(USER_WORD_LIMIT))),
        ))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    try:
        asyncio.run(collect_stats())

    except KeyboardInterrupt:
        print('\n[ Program Interrupted. ]')
