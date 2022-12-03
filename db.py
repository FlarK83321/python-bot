import peewee as pw
import json


db = pw.SqliteDatabase('db.sqlite3')


class Model(pw.Model):
	answers = pw.TextField(default='')
	passed = pw.BooleanField(default=False)

	def upload(self, answers:dict):
		self.answers = json.dumps(answers)

	def download(self):
		return json.loads(self.answers)


	class Meta:
		database = db


class Receiver(pw.Model):
	uid = pw.IntegerField()


	class Meta:
		database = db
	

class Account(Model):
	uid = pw.IntegerField()


class Interview(Model):
	uid = pw.IntegerField()


db.create_tables([Receiver, Account, Interview])