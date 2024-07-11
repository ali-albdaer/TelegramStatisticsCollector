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
    from unidecode import unidecode


logging.basicConfig(level=logging.WARNING)


if not os.path.exists('data'):
    os.makedirs('data')

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
        self.messages = dict()  # All messages sent by the user.
        self.word_counter = Counter()  # All words used by the user.
        self.daily_message_counter = Counter()  # Number of messages sent per day.
        self.category_words = defaultdict(Counter)  # Keywords and phrases.
        self.reactions_given = Counter()
        self.reactions_received = Counter()
        self.total_string = ''  # All messages concatenated.

    def calculate_ratios(self):
        curses = self.category_words.get('curses', Counter())
        self.curse_count = sum(curses.values())
        self.message_count = len(self.messages)

        self.activeness = len(self.daily_message_counter) / self.message_count if self.message_count else 0
        self.media_ratio = (self.media_count * 100) / self.message_count if self.message_count else 0
        self.loudness = (self.loud_message_count * 100) / self.message_count if self.message_count else 0
        self.naughtiness = (self.curse_count * 100) / self.message_count if self.message_count else 0

        return self.message_count, self.activeness, self.media_ratio, self.loudness, self.naughtiness


def count_category_sets(text, user_category_words: dict, global_stats: dict):
    top_categories = global_stats["top_categories"]

    for category, elements in category_sets.items():
        for element in elements:
            if isinstance(element, tuple):
                primary_key = element[0]
                aliases = element[1:]

            else:
                primary_key = element
                aliases = ()
            
            pattern = r'\b(?:{})\b'.format('|'.join([re.escape(alias) for alias in (primary_key,) + aliases]))
            count = len(re.findall(pattern, text))
            
            if count > 0:
                if isinstance(element, tuple):
                    primary_key = element[0]

                else:
                    primary_key = element
                    
                top_categories[category][primary_key] += count
                user_category_words[category][primary_key] += count
    
    
def fetch_message_stats(message, user_stats: dict, global_stats: dict):
    sender_id = message.sender_id
    user = user_stats[sender_id]
    user.messages[message.id] = message

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

    if not message.text:
        return
    
    if CONVERT_UNICODE:
        text = unidecode(message.text)

    else:
        text = message.text.encode('utf-8', errors='replace').decode('utf-8')

    if GET_CHANNEL_LOG:
        with open(log_channel_file, 'a', encoding='utf-8') as file:
            file.write(f'{user.name}: {text}\n')

    if text.isupper():
        user.loud_message_count += 1

    if CASE_INSENSITIVE:
        text = text.lower()

    if IGNORE_URLS:
        text = re.sub(r'http\S+', ' ', text)

    # Pattern for matching mentions, [name](tg://user?id=id)
    pattern = r'\[(.*?)\]\(tg://user\?id=(\d+)\)'
    match = re.search(pattern, text)

    if match:
        name = match.group(1)
        #user_id = match.group(2)
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

    # Update the total string for category matching and add a space between messages.
    user.total_string += text + '\n\n'


async def collect_stats():
    await telegram_client.connect()

    if not await telegram_client.is_user_authorized():
        await telegram_client.send_code_request(telegram_phone)
        await telegram_client.sign_in(telegram_phone, input('Enter the code you received on Telegram: '))

    group_entity = await telegram_client.get_entity(telegram_group_id)

    user_stats = {}
    global_stats = {
        'message_count': 0,
        'word_count': 0,
        'letter_count': 0,
        'top_words': Counter(),
        'active_users': dict(),
        'media_users': dict(),
        'loud_users': dict(),
        'cursing_users': dict(),
        'top_categories': defaultdict(Counter),
        'top_reactions': Counter()
    }

    total_messages = (await telegram_client.get_messages(group_entity, limit=0)).total
    processed_messages = 0

    async for message in telegram_client.iter_messages(group_entity):
        if not message.sender_id:  # Skip messages from deleted accounts.
            continue

        if message.sender_id not in user_stats:
            user_stats[message.sender_id] = User(message.sender_id)

        fetch_message_stats(message, user_stats, global_stats)

        processed_messages += 1
        if SHOW_PROGRESS_BAR:
            print(f'\rProcessed Messages: [{processed_messages} / {total_messages}]', end='')

    if SHOW_PROGRESS_BAR:
        print()

    for user in user_stats.values():
        count_category_sets(user.total_string, user.category_words, global_stats)
        message_count, activeness, media_ratio, loudness, naughtiness = user.calculate_ratios()
        global_stats['message_count'] += message_count

        if activeness:
            global_stats['active_users'][user.user_id] = user

        if media_ratio:
            global_stats['media_users'][user.user_id] = user

        if loudness:
            global_stats['loud_users'][user.user_id] = user

        if naughtiness:
            global_stats['cursing_users'][user.user_id] = user

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
    limited_top_active_users = sorted(global_stats['active_users'].items(), key=lambda x: x[1].activeness, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_media_users = sorted(global_stats['media_users'].items(), key=lambda x: x[1].media_ratio if GLOBAL_RANKING_BY_RATIO else x[1].media_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_loud_users = sorted(global_stats['loud_users'].items(), key=lambda x: x[1].loudness if GLOBAL_RANKING_BY_RATIO else x[1].loud_message_count, reverse=True)[:GLOBAL_RANKING_LIMIT]
    limited_top_cursing_users = sorted(global_stats['cursing_users'].items(), key=lambda x: x[1].naughtiness if GLOBAL_RANKING_BY_RATIO else x[1].curse_count, reverse=True)[:GLOBAL_RANKING_LIMIT]

    json_global_stats = {
        'message_count': global_stats['message_count'],
        'word_count': global_stats['word_count'],
        'letter_count': global_stats['letter_count'],
        'top_words': dict(global_stats['top_words'].most_common(GLOBAL_WORD_LIMIT)),
        'top_active_users': {user_id: {'name': user.name, 'activeness': user.activeness} for user_id, user in limited_top_active_users},
        'top_loud_users': {user_id: {'name': user.name, 'loudness': user.loudness, 'loud_message_count': user.loud_message_count} for user_id, user in limited_top_loud_users},
        'top_media_users': {user_id: {'name': user.name, 'media_ratio': user.media_ratio, 'media_count': user.media_count} for user_id, user in limited_top_media_users},
        'top_cursing_users': {user_id: {'name': user.name, 'naughtiness': user.naughtiness, 'curse_count': user.curse_count} for user_id, user in limited_top_cursing_users},
        'top_categories': {k: dict(v.most_common(GLOBAL_CATEGORY_LIMIT)) for k, v in global_stats['top_categories'].items()},
        'top_reactions': dict(global_stats['top_reactions'].most_common(GLOBAL_REACTION_LIMIT))
    }

    with open(global_stats_json, 'w', encoding='utf-8') as file:
        json.dump(json_global_stats, file, indent=4, ensure_ascii=False)


def save_user_stats(user_stats: dict):
    with open(user_stats_json, 'w', encoding='utf-8') as file:
        limited_user_stats = {
            user_id: {
                'user_id': user.user_id,
                'name': user.name,
                'message_count': user.message_count,
                'word_count': user.word_count,
                'letter_count': user.letter_count,
                'activeness': user.activeness,
                'media_count': user.media_count,
                'media_ratio': user.media_ratio,
                'loud_message_count': user.loud_message_count,
                'loudness': user.loudness,
                'curse_count': user.curse_count,
                'naughtiness': user.naughtiness,
                'top_active_days': dict(user.daily_message_counter.most_common(USER_ACTIVE_DAYS_LIMIT)),
                'top_category_words': {k: dict(v.most_common(USER_CATEGORY_LIMIT)) for k, v in user.category_words.items()},
                'top_words': dict(user.word_counter.most_common(USER_WORD_LIMIT)),
                'top_reactions_given': dict(user.reactions_given.most_common(USER_REACTION_LIMIT)),
                'top_reactions_received': dict(user.reactions_received.most_common(USER_REACTION_LIMIT)),
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
            activenss REAL,
            media_count INTEGER,
            media_ratio REAL,
            loud_message_count INTEGER,
            loudness REAL,
            curse_count INTEGER,
            naughtiness REAL,
            top_active_days TEXT,
            top_words TEXT,
            top_reactions_given TEXT,
            top_reactions_received TEXT,
            top_category_words TEXT
        )
    ''')

    for user_id, user in user_stats.items():
        cursor.execute('''
            INSERT OR REPLACE INTO user_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, user.name, 
            user.message_count, user.word_count, user.letter_count, user.activeness,
            user.media_count, user.media_ratio,
            user.loud_message_count, user.loudness, 
            user.curse_count, user.naughtiness, 
            json.dumps(dict(user.daily_message_counter.most_common(USER_ACTIVE_DAYS_LIMIT))),
            json.dumps(dict(user.word_counter.most_common(USER_WORD_LIMIT))),
            json.dumps(dict(user.reactions_given.most_common(USER_REACTION_LIMIT))), 
            json.dumps(dict(user.reactions_received.most_common(USER_REACTION_LIMIT))),
            json.dumps({k: dict(v.most_common(USER_CATEGORY_LIMIT)) for k, v in user.category_words.items()}),
        ))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    asyncio.run(collect_stats())
