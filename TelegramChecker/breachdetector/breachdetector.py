from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest, GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import sys
import os
import re
import html
lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
sys.path.append(lib_dir)
from lib.file_format import *

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(lib_dir)
from user_config import API_ID, API_HASH, PHONE_NUMBER, CZ_REGEX

import sqlite3

# api_hash from https://my.telegram.org, under API Development.
OUTPUT = "message_log.json"

CHANNEL_NAME = 'breachdetector'
OPTION_FILE = "options.json"
DB_FILE = "results.db"

from telethon import TelegramClient

def db_init():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        msg_id INTEGER PRIMARY KEY,
                        channel_name TEXT,
                        date TEXT,
                        source TEXT,
                        content TEXT,
                        author TEXT,
                        detection_date TEXT,
                        type TEXT
                    )''')
    conn.commit()
    conn.close()

def add_or_ignore_message(msg_json):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT 1 FROM messages WHERE msg_id = ?)", (msg_json['msg_id'],))
    result = cursor.fetchone()[0]

    if not result:
        cursor.execute('''INSERT INTO messages (msg_id, channel_name, date, source, content, author, detection_date, type)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (msg_json['msg_id'], msg_json['channel_name'], msg_json['date'], msg_json['source'],
                        msg_json['content'], msg_json['author'], msg_json['detection_date'], msg_json['type']))

    conn.commit()
    conn.close()

client = TelegramClient('userbot', API_ID, API_HASH)

async def save_messages(messages):

    for message in messages:
        msg = re.sub(r'<.*?>', r' ', message.message)
        msg = re.sub(r'\\', r' ', msg)
        match = re.search(r"({.*})", msg, re.DOTALL)

        if not match:
            print("No JSON object found in the text.", file=sys.stderr)
            print(message.message, file=sys.stderr)
            continue
        try:
            in_json = json.loads(match.group(1))

            msg_json = {
                "channel_name": CHANNEL_NAME,
                "date": str(message.date),
                "msg_id": message.id,
                "source": in_json["Source"],
                "content": in_json["Content"],
                "author": html.unescape(in_json["author"]),
                "detection_date": in_json["Detection Date"],
                "type": in_json["Type"]
            }
            add_or_ignore_message(msg_json)
        except json.decoder.JSONDecodeError as e:
            print(message.message)
            print(e.msg)


async def save_all_after(channel, after, max=10000, offset_id=0):
    req_count = 0
    end=False
    while req_count < max:
        all_messages = []
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=100,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        for message in history.messages:
            if message.date.replace(tzinfo=None) <= after:
                print(f"Time end, last_time will be saved")
                end = True
                break
            if message.message is None:
                print(f"message is {message}", file=sys.stderr)
                continue
            if re.search(CZ_REGEX, message.message.lower()):
                #print(all_messages)
                all_messages.append(message)
        if all_messages:
            await save_messages(all_messages)

        if end:
            break
        offset_id = history.messages[-1].id
        print(offset_id)
        req_count += 1


async def main():
    await client.start(phone=PHONE_NUMBER)

    channel = await client.get_entity(CHANNEL_NAME)
    print(f"Channel: \"{channel.title}\" {channel.id} {channel.access_hash} ", file=sys.stderr)

    last_time_posts_str = load_config(OPTION_FILE, "last_time_list", "0001-01-01 00:00:00")
    last_time_posts = datetime.datetime.strptime(last_time_posts_str, "%Y-%m-%d %H:%M:%S")
    db_init()
    await save_all_after(channel, last_time_posts, 1000, offset_id=0)
    update_config(OPTION_FILE, "last_time_list", now_string())


with client:
    client.loop.run_until_complete(main())