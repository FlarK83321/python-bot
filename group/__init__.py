# coding: utf8

'''Group bot'''


from pathlib import Path
from vkbottle import (
	KeyboardButtonColor,
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


sys.path.append(str(Path(__file__).parent.parent.parent))


path = Path(__file__).parent.parent.name

_send = __import__(f'{path}.account.send',
	globals(), locals(), ['send', 'send_to_interview'])
send, send_to_interview = _send.send, _send.send_to_interview
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


answer = '\n'.join([
	'Я тебя не понимаю 😟',
	'Нажми на кнопку с ответом 👆',
])


class Poll(BaseStateGroup):
	question0 = json.dumps({
		'index': 0,
		'question': 'Твоя деятельность связана с IT-сферой?',
		'answers': {
			'Связана': {
				'index': 1,
				'color': 'KeyboardButtonColor.POSITIVE',
			},
			'Не связана': {
				'index': 7,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
		},
	})
	question1 = json.dumps({
		'index': 1,
		'question': 'Поддерживаешь связь с единомышленниками?',
		'answers': {
			'Поддерживаю': {
				'index': 2,
				'color': 'KeyboardButtonColor.POSITIVE',
			},
			'Не поддерживаю': {
				'index': 9,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
		},
	})
	question2 = json.dumps({
		'index': 2,
		'question': 'Чаще общаешься в соцсетях или вживую?',
		'answers': {
			'Соцсети': {
				'index': 3,
				'color': 'KeyboardButtonColor.POSITIVE',
			},
			'Вживую': {
				'index': 5,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
		},
	})
	question3 = json.dumps({
		'index': 3,
		'question': 'Какие соцсети для IT-шников ты используешь?',
		'answers': {
			None: {
				'index': 4,
			},
		},
	})
	question4 = json.dumps({
		'index': 4,
		'question': 'Чем они привлекли твоё внимание?',
		'answers': {
			'Не знаю': {
				'index': 8,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
			None: {
				'index': 8,
			},
		},
	})
	question5 = json.dumps({
		'index': 5,
		'question': 'Знаешь ли ты какие-нибудь соцсети для IT-шников?',
		'answers': {
			'Не знаю': {
				'index': 10,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
			None: {
				'index': 6,
			},
		},
	})
	question6 = json.dumps({
		'index': 6,
		'question': 'Почему ты их не используешь?',
		'answers': {
			'Не знаю': {
				'index': 10,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
			None: {
				'index': 10,
			},
		},
	})

	question7 = json.dumps({
		'index': 7,
		'question': 'Какие соцсети для IT-шников ты знаешь?',
		'answers': {
			'Никакие': {
				'index': 10,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
			None: {
				'index': 10,
			},
		},
	})
	question8 = json.dumps({
		'index': 8,
		'question': 'Почему тебе нравится именно такой вид общения?',
		'answers': {
			'Не знаю': {
				'index': 10,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
			None: {
				'index': 10,
			},
		},
	})
	question9 = json.dumps({
		'index': 9,
		'question': 'В чём причина твоей ассоциальности?',
		'answers': {
			'Не знаю': {
				'index': 5,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
			None: {
				'index': 5,
			},
		},
	})
	question10 = json.dumps({
		'index': 10,
		'question': 'Как думаешь, коммуницирование IT-шников между собой способствует развитию IT-сферы?',
		'answers': {
			'Способствует': {
				'index': 11,
				'color': 'KeyboardButtonColor.POSITIVE',
			},
			'Не способствует': {
				'index': 11,
				'color': 'KeyboardButtonColor.NEGATIVE',
			},
		},
	})
	question11 = json.dumps({
		'index': 11,
		'question': 'Почему ты так считаешь?',
		'answers': {},
	})

	async def start(message):
		account, created = db.Account.get_or_create(uid=message.peer_id)

		if not created:
			return 'Опрос уже пройден'

		state = Poll.question0

		await bot.state_dispenser.set(message.peer_id, state)

		state = json.loads(state)
		_answer = state['question']

		keyboard = Keyboard(one_time=False, inline=True)
		answers = state['answers']

		for ans in answers:
			if ans:
				keyboard.add(Text(ans), color=eval(answers[ans]['color']))

		return await message.answer(_answer, keyboard=keyboard)


	async def end(message):
		await bot.state_dispenser.delete(message.peer_id)

		ctx.set(Poll.question11, message.text)

		account = save_storage(message.peer_id, ctx)
		account.passed = True
		account.save()

		_answer = 'Спасибо за помощь ♡'


		async def _account_send():
			'''Благодарит account-bot'''

			await send(
				dict(
					sticker_id=random.choice([73092, 73077]),
					user_id=message.peer_id, random_id=0),
				)
			if account.download()[Poll.question0] == 'Связана':
				await send_to_interview(account)


		async def _send():
			'''Благодарит group-bot'''

			await message.answer(_answer, keyboard=Keyboard())
			await message.answer(sticker_id=73062, keyboard=Keyboard())


		return '' if (await asyncio.wait([
			_account_send(),
			_send(),
		])) else ''

	@classmethod
	def questions(cls):
		'''Возвращает список всех stats'''

		return [
			cls.question0, cls.question1, cls.question2,
			cls.question3, cls.question4, cls.question5,
			cls.question6, cls.question7, cls.question8,
			cls.question9, cls.question10, cls.question11,
		]

	@classmethod
	def setup(cls):
		questions = cls.questions()

		def model(_question):
			'''Инициализирует стандартный state-обработчик'''

			question = json.loads(_question)

			def get_question(q):
				'''Получить значение state'''
				return eval(f'Poll.question{q["index"]}')

			async def wrapper(message):
				'''Оболочка стандартного state-обработчика'''

				if message.text in question['answers']:
					next_question = get_question(question['answers'].get(message.text))
				elif 'null' in question['answers']:
					next_question = get_question(question['answers'].get('null'))
				else:
					return answer

				await bot.state_dispenser.set(message.peer_id, next_question)
				next_question = json.loads(next_question)

				keyboard = Keyboard(one_time=False, inline=True)
				for ans in next_question['answers']:
					if ans != 'null':
						keyboard.add(Text(ans), color=eval(next_question['answers'][ans]['color']))
				
				ctx.set(_question, message.text)

				return await message.answer(next_question['question'], keyboard=keyboard)

			bot.on.private_message(state=_question)(wrapper)

		bot.on.private_message(lev='начать')(cls.start)

		for question in questions[:-1]:
			model(question)

		bot.on.private_message(state=questions[-1])(cls.end)


def save_storage(uid, ctx):
	'''Сохраняет данные опроса'''

	account = db.Account.get(uid=uid)

	storage = dict([
		(question, ctx.get(question))
		for question in Poll.questions()
	])

	account.upload(ctx.storage or storage)

	return account