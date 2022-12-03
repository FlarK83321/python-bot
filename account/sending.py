# coding: utf8

'''Sending to suggestions'''


from pathlib import Path
import asyncio
import random
import sys


sys.path.append(str(Path(__file__).parent.parent.parent))


path = Path(__file__).parent.parent.name

send = __import__(f'{path}.account.send',
	globals(), locals(), ['send']).send
bot = __import__(f'{path}.account',
	globals(), locals(), ['bot']).bot
db = __import__(f'{path}', globals(), locals(), ['db']).db


message = '''
Пройди, пожалуйста, опрос
Мне для проекта нужно🙏
Просто напиши боту "Начать"
👉 @flummox.team
		'''.strip()


async def main(batch, ids=[]):
	'''Отправляет сообщения сначать пользователям ids,
		а потом возможным друзьям в количестве batch'''


	async def sending(_id):
		if db.Receiver.get_or_none(uid=_id):
			return

		code = await send(
			dict(user_id=_id,
				sticker_id=random.choice([73055, 73071]),
				random_id=0),
			timeout=(random.randint(1_000, 3_000) / 1000),
			)
		code = await send(
			dict(user_id=_id,
				message=message,
				random_id=0),
			timeout=(random.randint(3_000, 5_000) / 1000),
			)
		code = await send(
			dict(user_id=_id,
				sticker_id=73100,
				random_id=0),
			timeout=(random.randint(5_000, 10_000) / 1000),
			)

		receiver = db.Receiver.create(uid=_id)

	for _id in ids:
		await sending(_id)

	if not batch:
		return

	for index, suggestion in enumerate((await bot.api.friends.get_suggestions(count=batch)).items):
		await sending(suggestion.id)


if __name__ == '__main__':
	while True:
		asyncio.new_event_loop().run_until_complete(main())