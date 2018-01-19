#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*     Domain     *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')
import time, asyncio
from datetime import datetime
from orm import IntegeField, StringField, Model

def next_id():
	return int('%15d000' % (time.time() * 1000))

class User(Model):
	id = IntegeField(name = 'id', primary_key=True, default=next_id)
	name = StringField(name='name')
	password = StringField(name='password')
	email = StringField(name='email')
	admin = IntegeField(name='admin', column_type='Number(1)', default=0)
	image = StringField(name='image')
	create_time = StringField(name='create_time', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
#	create_time = StringField(name='create_time', default=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f'))

class Blog(Model):
	id = IntegeField(name = 'id', primary_key=True, default=next_id)
	user_id = IntegeField(name = 'id')
	name = StringField(name='name')
	summary = StringField(name='summary')
	content = StringField(name='content')
	create_time = StringField(name='create_time', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))

class Comment(Model):
	id = IntegeField(name = 'id', primary_key=True, default=next_id)
	user_id = IntegeField(name = 'id')
	blog_id = IntegeField(name = 'id')
	content = StringField(name='content')
	create_time = StringField(name='create_time', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
		

def run():
#	user = User(name='qpf3', email='qpf0510@qq.com')
#	res = yield from user.save()
#	print(res)
	rows = yield from User().find()
	for row in rows:
		print(row)

def start_server():
	loop = asyncio.get_event_loop()
	loop.run_until_complete(run())
	loop.run_forever()

if __name__ == '__main__':
	print(__doc__ % __author__)
	
	start_server()
	
#	user = User(name='shadaileng', password='123456', email='qpf0510@qq.com', admin=0, image='./res/tumblr.png')
#	user.save()
	
#	user = User(name='shadileng', email='qpf0510@qq.com')
#	user.delete()
#	rows = User().find()
#	for row in rows:
#		print(row)
	
#	user = User(id = '2', name='shadileng', email='qpf0510@qq.com')
#	user.update()
	
#	user = User(name='qpf', password='123456', email='qpf0510@qq.com', admin=0, image='./res/tumblr.png')
#	print(user)
#	res = user.save()
#	print('res: %s' % res)
