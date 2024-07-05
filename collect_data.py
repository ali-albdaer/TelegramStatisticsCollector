import os
import json
import logging
import asyncio
import re
import sqlite3
from collections import Counter, defaultdict
from telethon import TelegramClient

from config import *
from lookup import category_sets, ignored_words, curses


if CONVERT_UNICODE:
    from unidecode import unidecode


logging.basicConfig(level=logging.INFO)


if not os.path.exists('data'):
    os.makedirs('data')


telegram_client = TelegramClient(session_file, api_id, api_hash)


class User:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.name = None
        self.message_count = 0
        self.media_count = 0
        self.word_count = 0
        self.word_counter = Counter()  # Counts all words then chooses the top TOP_WORDS_LIMIT
        self.letter_count = 0
        self.loud_messages = 0
        self.curses_count = 0
        self.daily_activity = Counter()
        self.category_words = defaultdict(Counter)
        self.reactions_given = Counter()
        self.reactions_received = Counter()

    def calculate_ratios(self):
        self.loudness = self.loud_messages / self.message_count if self.message_count else 0
        self.naughtiness = self.curses_count / self.message_count if self.message_count else 0

    def top_words(self, n):
        return dict(self.word_counter.most_common(n))

def fetch_message_stats(message, user_stats: dict, global_stats: dict, category_sets: dict):
    sender_id = message.sender_id
    user = user_stats[sender_id]
    user.message_count += 1

    if not user.name:
        user.name = message.sender.first_name + (' ' + message.sender.last_name if message.sender.last_name else '')

    date_str = message.date.strftime('%Y-%m-%d')
    user.daily_activity[date_str] += 1

    if message.media:
        user.media_count += 1
        global_stats['media_users'][sender_id] += 1

    if message.text:
        if CONVERT_UNICODE:
            text = unidecode(message.text)

        else:
            text = message.text

        if CASE_INSENSITIVE:
            text = text.lower()

        words = re.findall(r'\b\w+\b', text)
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

        if text.isupper():
            user.loud_messages += 1
            global_stats['loud_users'][sender_id] += 1

        for category, elements in category_sets.items():
            for element in elements:
                was_found = False

                if isinstance(element, tuple):
                    for alias in element:
                        if ' ' in alias:
                            _count = text.count(alias)
                            if _count > 0:
                                global_stats['category_mentions'][category][element[0]] += _count
                                was_found = True

                        elif not was_found and alias in words:
                            _count = words.count(alias)
                            if _count > 0:
                                user.category_words[category][element[0]] += _count
                                global_stats['category_mentions'][category][element[0]] += _count

                else:
                    if ' ' in element:
                        _count = text.count(element)
                        if _count > 0:
                            global_stats['category_mentions'][category][element] += _count
                            was_found = True

                    elif not was_found and element in words:
                        _count = words.count(element)
                        if _count > 0:
                            user.category_words[category][element] += _count
                            global_stats['category_mentions'][category][element] += _count

        for curse in curses:
            if curse in words:
                user.curses_count += words.count(curse)
                global_stats['cursing_users'][sender_id] += words.count(curse)

    if COUNT_REACTIONS and hasattr(message, 'reactions') and message.reactions:
        for reaction in message.reactions.recent_reactions:
            if reaction.peer_id:
                user_stats[reaction.peer_id.user_id].reactions_given[reaction.reaction.emoticon] += 1

            user.reactions_received[reaction.reaction.emoticon] += 1
            global_stats['top_reactions'][reaction.reaction.emoticon] += 1


async def collect_stats():
    await telegram_client.connect()

    if not await telegram_client.is_user_authorized():
        await telegram_client.send_code_request(telegram_phone)
        await telegram_client.sign_in(telegram_phone, input('Enter the code you received on Telegram: '))

    group_entity = await telegram_client.get_entity(telegram_group_id)

    user_stats = defaultdict(User)
    global_stats = {
        'message_count': 0,
        'word_count': 0,
        'letter_count': 0,
        'top_words': Counter(),
        'loud_users': Counter(),
        'media_users': Counter(),
        'cursing_users': Counter(),
        'category_mentions': defaultdict(Counter),
        'top_reactions': Counter()  # Global reaction statistics
    }

    total_messages = (await telegram_client.get_messages(group_entity, limit=0)).total
    global_stats['message_count'] = total_messages
    processed_messages = 0

    async for message in telegram_client.iter_messages(group_entity):
        if message.sender_id not in user_stats:
            user_stats[message.sender_id] = User(message.sender_id)

        fetch_message_stats(message, user_stats, global_stats, category_sets)

        processed_messages += 1
        if SHOW_PROGRESS_BAR:
            print(f'\rProcessed Messages: [{processed_messages} / {total_messages}]', end='')

    if SHOW_PROGRESS_BAR:
        print()

    for user in user_stats.values():
        user.calculate_ratios()

    save_global_stats(global_stats)
    save_user_stats(user_stats)

    await telegram_client.disconnect()

    if LOGOUT:
        os.remove(session_file)

    print('[ Program Finished. ]')

def save_global_stats(global_stats: dict):
    json_global_stats = {
        'message_count': global_stats['message_count'],
        'word_count': global_stats['word_count'],
        'letter_count': global_stats['letter_count'],
        'top_words': dict(global_stats['top_words'].most_common(GLOBAL_MESSAGE_LIMIT)),
        'loud_users': dict(global_stats['loud_users'].most_common(GLOBAL_RANKING_LIMIT)),
        'media_users': dict(global_stats['media_users'].most_common(GLOBAL_RANKING_LIMIT)),
        'cursing_users': dict(global_stats['cursing_users'].most_common(GLOBAL_RANKING_LIMIT)),
        'category_mentions': {k: dict(v.most_common(CATEGORY_MENTION_LIMIT)) for k, v in global_stats['category_mentions'].items()},
        'top_reactions': dict(global_stats['top_reactions'].most_common(TOP_REACTION_LIMIT))
    }

    with open(global_stats_json, 'w') as file:
        json.dump(json_global_stats, file, indent=4)

def save_user_stats(user_stats: dict):
    with open(user_stats_json, 'w') as file:
        limited_user_stats = {
            user_id: {
                'user_id': user.user_id,
                'name': user.name,
                'message_count': user.message_count,
                'media_count': user.media_count,
                'word_count': user.word_count,
                'letter_count': user.letter_count,
                'loud_messages': user.loud_messages,
                'loudness': user.loudness,
                'curses_count': user.curses_count,
                'naughtiness': user.naughtiness,
                'daily_activity': dict(user.daily_activity.most_common(TOP_ACTIVE_DAYS_LIMIT)),
                'category_words': {k: dict(v) for k, v in user.category_words.items()},
                'top_words': user.top_words(TOP_WORD_LIMIT),
                'reactions_given': dict(user.reactions_given),  # Include reactions given by the user
                'reactions_received': dict(user.reactions_received),  # Include reactions received by the user
            }
            for user_id, user in user_stats.items()
        }
        json.dump(limited_user_stats, file, indent=4)

    conn = sqlite3.connect(user_stats_db)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            message_count INTEGER,
            media_count INTEGER,
            word_count INTEGER,
            letter_count INTEGER,
            loud_messages INTEGER,
            loudness REAL,
            curses_count INTEGER,
            naughtiness REAL,
            daily_activity TEXT,
            category_words TEXT,
            top_words TEXT,
            reactions_given TEXT,
            reactions_received TEXT
        )
    ''')

    for user_id, user in user_stats.items():
        cursor.execute('''
            INSERT OR REPLACE INTO user_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.user_id, user.name, user.message_count, user.media_count,
            user.word_count, user.letter_count, user.loud_messages, user.loudness, user.curses_count, user.naughtiness,
            json.dumps(dict(user.daily_activity.most_common(TOP_ACTIVE_DAYS_LIMIT))),
            json.dumps({k: dict(v) for k, v in user.category_words.items()}), json.dumps(user.top_words(TOP_WORD_LIMIT)),
            json.dumps(dict(user.reactions_given)), json.dumps(dict(user.reactions_received)),
        ))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    asyncio.run(collect_stats())
