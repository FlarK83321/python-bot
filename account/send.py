# coding: utf8

'''Модуль отправки сообщения пользователю'''

from vkbottle import VKAPIError
from pathlib import Path
import asyncio
import random
import sys


sys.path.append(str(Path(__file__).parent.parent.parent))


path = Path(__file__).parent.parent.name

_account = __import__(f'{path}.account',
	globals(), locals(), ['bot', 'Interview'])
bot, Interview = _account.bot, _account.Interview
db = __import__(f'{path}', globals(), locals(), ['db']).db


async def send(api, *args, timeout=(random.randint(3_000, 10_000) / 1000),
		error_timeout=300, error_level=0, **kwargs):
	'''Пытается отправить сообщение пользователю
		!пережидает капчи!'''

	async def wrapper(level):
		event = key = value = None

		try:
			code = await bot.api.messages.send(**api)

			key = 'message'
			value = '{timeout}s'
		except VKAPIError as error:
			key = f'{error.__class__.__name__}'

			if isinstance(error, CaptchaError):
				level += 1

				value = ' as '.join([
					''.join(['(', f'{level}']),
					''.join([value, ')']),
				])
			else:
				value = '{timeout}s'

			code = None
		else:
			if level:
				level -= .1
		finally:
			event = f'<{key} at {value}>'

			return code, event, level


	code, event, error_level = await wrapper(error_level)

	while not code:
		_timeout = error_timeout * (int(error_level) ** .75)

		print(event.format(timeout=_timeout))
		event = None
		
		await asyncio.sleep(_timeout)

		code, event, error_level = await wrapper(error_level)

	timeout = random.randint(3_000, 10_000) / 1000
	print(event.format(timeout=timeout))

	await asyncio.sleep(timeout)

	return code


async def send_to_interview(account):
	'''Отправляет пользователю первый вопрос интервью'''
	
	interview, created = db.Interview.get_or_create(uid=account.uid)

	if not created:
		return

	message = f'''
Как я понимаю, ты программист
{Interview.question0}
	'''

	await send(
		dict(user_id=account.uid,
			message=message,
			random_id=0),
		)