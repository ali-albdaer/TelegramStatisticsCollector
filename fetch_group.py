import os
import sqlite3
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import PeerUser
from res.config import *
import asyncio


logging.basicConfig(level=logging.INFO)


telegram_client = TelegramClient(session_file, api_id, api_hash)


class Reaction:
    def __init__(self, peer_id, reaction):
        self.peer_id = peer_id
        self.reaction = reaction


class Message:
    def __init__(self, message_id, sender_id, sender, text, date, media, reactions):
        self.id = message_id
        self.sender_id = sender_id
        self.sender = sender
        self.text = text
        self.date = date
        self.media = media
        self.reactions = reactions


class User:
    def __init__(self, user_id, first_name=None, last_name=None, username=None):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    @property
    def name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or "Unknown User"
    

def process_message(message, conn, cursor):
    user = message.sender
    text = message.text or ''
    date = message.date.strftime('%Y-%m-%d %H:%M:%S')
    media = int(bool(message.media))
    reactions = str([(reaction.peer_id.user_id, reaction.reaction.emoticon) for reaction in message.reactions.recent_reactions]) if message.reactions and message.reactions.recent_reactions else ''

    cursor.execute('''
        INSERT OR REPLACE INTO messages (message_id, sender_id, text, date, media, reactions)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (message.id, message.sender_id, text, date, media, reactions))

    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
    ''', (user.id, user.first_name, user.last_name, user.username))

    cursor.execute('''
        INSERT OR REPLACE INTO meta (key, value)
        VALUES ("last_message_id", ?)
    ''', (message.id,))

    cursor.execute('UPDATE meta SET value = ? WHERE key = "last_message_id"', (message.id,))

    conn.commit()


async def fetch_messages():
    await telegram_client.connect()

    if not await telegram_client.is_user_authorized():
        await telegram_client.send_code_request(telegram_phone)
        await telegram_client.sign_in(telegram_phone, input('Enter the code you received on Telegram: '))

    group_entity = await telegram_client.get_entity(telegram_group_id)

    conn = sqlite3.connect(messages_db)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY,
            sender_id INTEGER,
            text TEXT,
            date TEXT,
            media INTEGER,
            reactions TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    if SHOW_PROGRESS_BAR:
        latest_message = await telegram_client.get_messages(group_entity, limit=1)
        first_message = await telegram_client.get_messages(group_entity, limit=1, reverse=True)

        latest_message_id = latest_message[0].id if latest_message else 0
        first_message_id = first_message[0].id if first_message else 0
        processed_messages = 0

    cursor.execute('SELECT value FROM meta WHERE key = "last_message_id"')
    row = cursor.fetchone()
    last_message_id = int(row[0]) if row else 0

    batch_size = 100
    min_id = last_message_id

    while True:
        messages = await telegram_client.get_messages(group_entity, min_id=min_id, limit=batch_size, reverse=True)
        if not messages:
            break

        for message in messages:
            if not message.sender:  # Ignore system messages.
                continue

            process_message(message, conn, cursor)
            processed_messages += 1

            if SHOW_PROGRESS_BAR:
                if latest_message_id and first_message_id:  # Avoid division by zero for the first message.
                    percentage = round(((message.id - first_message_id) / (latest_message_id - first_message_id)) * 100, 2)
                    print(f'\rProcessed Messages: [{message.id - first_message_id} / {latest_message_id - first_message_id}] [{percentage}%]', end='')

            min_id = message.id

    if SHOW_PROGRESS_BAR:
        print()

    logging.info('Closing Database and disconnecting from Telegram...')
    conn.close()
    await telegram_client.disconnect()


def get_messages():
    conn = sqlite3.connect(messages_db)
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, first_name, last_name, username FROM users')
    users = {user_id: User(user_id, first_name, last_name, username) for user_id, first_name, last_name, username in cursor.fetchall()}

    cursor.execute('SELECT message_id, sender_id, text, date, media, reactions FROM messages ORDER BY message_id ASC')
    for row in cursor.fetchall():
        message_id, sender_id, text, date, media, reactions = row
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        reactions = [Reaction(PeerUser(peer_id), reaction) for peer_id, reaction in eval(reactions)] if reactions else []
        yield Message(message_id, sender_id, users[sender_id], text, date, media, reactions)

    conn.close()


if __name__ == '__main__':
    import time
    start = time.time()

    try:
        os.makedirs(output_folder, exist_ok=True)
        asyncio.run(fetch_messages())

    except KeyboardInterrupt:
        print('\n[ Program Interrupted. ]')
        print('There is a chance that the last message would be duplicated, please check the last entry after running the script again.')

    except Exception as e:
        print(f'\n[ Error: {e} ]')
        print('There is a chance that the last message would be duplicated, please check the last entry after running the script again.')

    else:
        print('\n[ Program Finished. ]')

    end = time.time()
    print(f'Execution Time: {end - start:.2f} seconds')
