import sys
import asyncio
from telethon import TelegramClient, events, sync
import re

# api_hash from https://my.telegram.org, under API Development.
api_id = 22859552
api_hash = '7e65ea367a7c27bf9559828fa38026a5'
OUTPUT = "message_log.json"
CZ_REGEX = r'cz | sk '
CHAT_ID = -1001518255631

client = TelegramClient('name', api_id, api_hash)

async def main():
    @client.on(events.NewMessage(chats=[CHAT_ID]))
    async def handler(event):
        print("Event Occured")
        if re.search(CZ_REGEX, event.raw_text.lower()):
            with open(OUTPUT, 'a') as file:
                file.write(event.raw_text + '\n')

    async def get_all_messages():
        async for message in client.iter_messages(CHAT_ID):
            if re.search(CZ_REGEX, message.raw_text.lower()):
                print(message.text)

    client.loop.run_until_complete(get_all_messages())
    client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
