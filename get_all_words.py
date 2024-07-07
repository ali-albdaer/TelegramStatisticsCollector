import os
import json
import asyncio
import re
from collections import Counter
from unidecode import unidecode

from telethon import TelegramClient
from res.config import *


if not os.path.exists('data'):
    os.makedirs('data')


async def collect_word_stats():
    await telegram_client.connect()

    if not await telegram_client.is_user_authorized():
        await telegram_client.send_code_request(telegram_phone)
        await telegram_client.sign_in(telegram_phone, input('Enter the code you received on Telegram: '))

    group_entity = await telegram_client.get_entity(telegram_group_id)

    all_words = Counter()
    all_words_lower = Counter()

    total_messages = (await telegram_client.get_messages(group_entity, limit=0)).total
    processed_messages = 0

    async for message in telegram_client.iter_messages(group_entity):
        if message.text:
            text = unidecode(message.text)  # Convert Unicode characters to ASCII
            words = re.findall(r'\b\w+\b', text)

            all_words.update(words)
            all_words_lower.update(word.lower() for word in words)

        processed_messages += 1
        print(f'\rProcessed Messages: [{processed_messages} / {total_messages}]', end='')

    await telegram_client.disconnect()

    print()  # Print newline after progress bar

    save_word_stats_json(sensitive_freq_json, dict(sorted(all_words.items(), key=lambda x: x[1], reverse=True)))
    save_word_stats_json(sensitive_alpha_json, dict(sorted(all_words.items(), key=lambda x: x[0])))
    save_word_stats_json(insensitive_freq_json, dict(sorted(all_words_lower.items(), key=lambda x: x[1], reverse=True)))
    save_word_stats_json(insensitive_alpha_json, dict(sorted(all_words_lower.items(), key=lambda x: x[0])))

    if LOGOUT:
        os.remove(session_file)

    print('[ Program Finished. ]')


def save_word_stats_json(filename, word_counter):
    with open(filename, 'w') as file:
        json.dump(word_counter, file, indent=4)


def save_word_stats_text(filename, word_counter):
    with open(filename, 'w') as file:
        file.write(str(word_counter))


if __name__ == '__main__':
    telegram_client = TelegramClient(session_file, api_id, api_hash)
    asyncio.run(collect_word_stats())
