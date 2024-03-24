import sys

from telethon import TelegramClient, events, sync
from telethon.errors import SessionPasswordNeededError
import re

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = 22859552
api_hash = '7e65ea367a7c27bf9559828fa38026a5'

OUTPUT = "message_log.json"
client = TelegramClient('anon', api_id, api_hash)
CZ_REGEX = r'cz | sk '
CHAT_ID = -1001518255631
@client.on(events.NewMessage(chats=[CHAT_ID]))
async def handler(event):
    print("Event Occured")
    # print(event.raw_text)
    if re.search(CZ_REGEX, event.raw_text.lower()):
        with open(OUTPUT, 'a') as file:
            file.write(event.raw_text + '\n')

async def get_all_messages():
    async for message in client.iter_messages(CHAT_ID):
        if re.search(CZ_REGEX, message.raw_text.lower()):
            print(message.text)

client.start()
if sys.argv[1] == 'all':
    client.loop.run_until_complete(get_all_messages())
client.run_until_disconnected()
