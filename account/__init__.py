# coding: utf-8

'''Account bot'''


from vkbottle import User as Bot, BaseStateGroup, CtxStorage
from aiohttp_socks import ProxyConnector
from vkbottle.http import AiohttpClient
from aiohttp import ClientSession
from vkbottle import API
from pathlib import Path
import asyncio
import random
import dill
import sys
import re


sys.path.append(str(Path(__file__).parent.parent.parent))


path = Path(__file__).parent.parent.name

db = __import__(f'{path}', globals(), locals(), ['db']).db


token = dill.load(open(Path(__file__).parent / '.access', 'rb'))


if '--test' in sys.argv or '-t' in sys.argv:
	bot = Bot(token=token)
else:
	connector = ProxyConnector.from_url("http://proxy.server:3128")
	session = ClientSession(connector = connector)
	proxy = AiohttpClient(session = session)
	
	api = API(token=token, http_client=proxy)

	bot = Bot(api=api)

ctx = CtxStorage()


class Interview(BaseStateGroup):
	question0 = 'Какой у тебя стаж?'
	question1 = 'А образование какое?'
	question2 = 'По какой специальности?'
	question3 = 'В каком направлении работаешь?'
	question4 = 'У тебя есть собственные проекты?\nЕсли есть, то сколько их?'
	question5 = 'Какой по-твоему должна быть соцсеть?\nСамые важные критерии?'
	question6 = 'Какие, на твой взгляд, проблемы должна решить соцсеть для программистов?'

	@classmethod
	def questions(cls):
		'''Возвращает список всех states'''

		return [
			cls.question0,
			cls.question1,
			cls.question2,
			cls.question3,
			cls.question4,
			cls.question5,
			cls.question6,
		]

	async def handle(message):
		'''Обработчик всех сообщений'''

		interview = db.Interview.get_or_none(uid=message.peer_id)
		if not interview:
			return

		if interview.passed:
			return

		question = await bot.state_dispenser.get(message.peer_id)
		if question:
			index = ctx.get("state") + 1
		else:
			index = 0

		ctx.set('state', index)
		question = Interview.__dict__[f'question{index}']

		if question == Interview.questions()[-1]:
			await bot.state_dispenser.delete(message.peer_id)
			
			interview = save_interview(message.peer_id, ctx)
			interview.passed = True
			interview.save()
			
			_answer = '' if (await asyncio.wait([
				message.answer('Спасибо ещё раз ♡'),
				message.answer(sticker_id=random.choice([73092, 73077])),
			])) else ''
		else:
			index = Interview.questions().index(question)
			
			next_question = Interview.questions()[index + 1]
			
			await bot.state_dispenser.set(message.peer_id, next_question)
			
			_answer = next_question

		ctx.set(Interview.question0, message.text)

		return _answer

	@classmethod
	def setup(cls):
		bot.on.private_message()(cls.handle)


def save_interview(uid, ctx):
	'''Сохраняет данные интервью'''

	interview = db.Interview.get(uid=uid)

	storage = dict([
		(question, ctx.get(question))
		for question in Interview.questions()
	])

	interview.upload(ctx.storage or storage)

	return interview


admins = []
status = None


@bot.on.private_message(peer_ids=admins, regex=r'(^[\\/][Оо] .+)|(^[\\/][Сс] (.+){2,})')
async def message_handler(message):
	'''Обрабатывает команды админа в реальном времени'''

	global status

	if status:
		return await status_handler(message)

	_sending = __import__(f'{path}.account.sending',
		globals(), locals(), ['sender'])
	sender, msg = _sending.main, _sending.message

	status = message.text.split()
	if re.match(r'[\\/][Оо]', status[0]):
		await sender(int(status[-1]))
	elif re.match(r'[\\/][Сс]', status[0]):
		await sender(0, [int(status[-1])])

	status = None

	return await message.answer(f'{message.text}\nВыполнено!')


@bot.on.private_message(peer_ids=admins, lev='статус')
async def status_handler(message):
	'''Отправляет статус выполнения команды'''

	return f'Выполняется\n{status}'