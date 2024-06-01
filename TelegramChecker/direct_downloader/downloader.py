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


