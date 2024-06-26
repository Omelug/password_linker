from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest, GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import sys
import os
import re
import html
from discord_webhook import DiscordWebhook

script_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(script_dir, '../..')
sys.path.append(lib_dir)
from lib.file_format import *

config_dir = os.path.join(script_dir, '..')
sys.path.append(config_dir)
from user_config import API_ID, API_HASH, PHONE_NUMBER, CZ_REGEX, SK_REGEX
import requests

import sqlite3

# api_hash from https://my.telegram.org, under API Development.
OUTPUT = "message_log.json"

CHANNEL_NAME = 'breachdetector'
OPTION_FILE = os.path.join(script_dir, "options.json")
DB_FILE = os.path.join(script_dir, "breachdetector.db")
DISCORD=True
DEFAULT_USERS = ["503629068319588407"]
WEBHOOK="https://discord.com/api/webhooks/1247872452617572486/xkbg2luX_48wKHElCLXpAjypx5Mvq1t_O57kfJknr6tWXrOnmdxU9h7P02BazwGnKRJ1"
from telethon import TelegramClient

def print_to_discord(msg="msg not set", ping=False, users=DEFAULT_USERS, std=False):
    if std:
        print(msg)
    if ping and users:
        for user_id in users:
            msg = f"<@{user_id}> {msg}"
    webhook = DiscordWebhook(url=WEBHOOK, content=msg)
    while True:
        try:
            response = webhook.execute()
            if response.status_code != 429:
                break
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:
                retry_after = err.response.json()['retry_after']
                time.sleep(retry_after+1)
            else:
                raise


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


async def save_all_after(channel, after, max=100000, offset_id=0):
    req_count = 0
    end=False
    new_leaks = 0
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
            #print(f"{message.date.replace(tzinfo=None)} <= {after} {message.date.replace(tzinfo=None) <= after:}")
            if message.date.replace(tzinfo=None) <= after:
                #print(f"Time end, last_time will be saved")
                end = True
                return new_leaks
            if message.message is None:
                print(f"message is {message}", file=sys.stderr)
                continue
            msg = message.message
            if re.search(CZ_REGEX, msg, re.IGNORECASE) or re.search(SK_REGEX, msg, re.IGNORECASE):
                if DISCORD:
                    print_to_discord(msg=message.message, ping=True)
                new_leaks += 1
                all_messages.append(message)

        if all_messages:
            await save_messages(all_messages)

        if end:
            break
        offset_id = history.messages[-1].id
        #print(offset_id)
        req_count += 1


async def main():
    channel = await client.get_entity(CHANNEL_NAME)
    #print(f"Channel: \"{channel.title}\" {channel.id} {channel.access_hash} ", file=sys.stderr)

    last_time_posts_str = load_config(OPTION_FILE, "last_time_list", "0001-01-01 00:00:00")
    last_time_posts = datetime.datetime.strptime(last_time_posts_str, "%Y-%m-%d %H:%M:%S")
    db_init()
    new_leaks = await save_all_after(channel, last_time_posts, offset_id=0)
    now = now_string()
    update_config(OPTION_FILE, "last_time_list", now)

    dalay_msg = f"Checked {last_time_posts_str} -> {now}\n({datetime.datetime.now() - last_time_posts})"
    print_to_discord(dalay_msg, std=True)
    if new_leaks:
        print_to_discord(f"{new_leaks} new leaks found {CZ_REGEX} {SK_REGEX}", std=True, ping=True)
client = TelegramClient('userbot', API_ID, API_HASH).start(phone=PHONE_NUMBER)
with client:
    client.loop.run_until_complete(main())