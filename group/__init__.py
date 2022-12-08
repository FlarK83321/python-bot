# coding: utf8

'''Group bot'''


from pathlib import Path
from vkbottle import (
	KeyboardButtonColor,
	DocMessagesUploader,
	BaseStateGroup,
	CtxStorage,
	Keyboard,
	Text,
	Bot,
)
from aiohttp_socks import ProxyConnector
from vkbottle.http import AiohttpClient
from aiohttp import ClientSession
from vkbottle import API
import asyncio
import random
import dill
import json
import sys
import os
import re


token = dill.load(open(Path(__file__).parent / '.access', 'rb'))

ctx = CtxStorage()

if '--test' in sys.argv or '-t' in sys.argv:
	bot = Bot(token=token)
else:
	connector = ProxyConnector.from_url("http://proxy.server:3128")
	session = ClientSession(connector = connector)
	proxy = AiohttpClient(session = session)

	api = API(token=token, http_client=proxy)

	bot = Bot(api=api)
