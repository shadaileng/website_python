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
import time, asyncio, sys
from datetime import datetime
from orm import IntegeField, StringField, Model

def next_id():
	return int('%15d000' % (time.time() * 1000))

class User(Model):
	id = IntegeField(name = 'id', primary_key=True, default=next_id)
	name = StringField(name='name')
	password = StringField(name='password')
	email = StringField(name='email')
	admin = IntegeField(name='admin', column_type='Number(2)', default=0)
	image = StringField(name='image')
	createtime = StringField(name='createtime', default=lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
	updatetime = StringField(name='updatetime', default=lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
#	create_time = StringField(name='create_time', default=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f'))

class Blog(Model):
	id = IntegeField(name = 'id', primary_key=True, default=next_id)
	userid = IntegeField(name = 'userid')
	name = StringField(name='name')
	summary = StringField(name='summary', column_type='Varchar(256)')
	content = StringField(name='content', column_type='Varchar(1024)')
	createtime = StringField(name='createtime', default=lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
	updatetime = StringField(name='updatetime', default=lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))

class Comment(Model):
	id = IntegeField(name = 'id', primary_key=True, default=next_id)
	userid = IntegeField(name = 'userid')
	blogid = IntegeField(name = 'blogid')
	content = StringField(name='content', column_type='Varchar(140)')
	createtime = StringField(name='createtime', default=lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
	updatetime = StringField(name='updatetime', default=lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))

class File(Model):
	hashpath = StringField(name='hashpath', primary_key=True)
	path = StringField(name='path')
	name = StringField(name='name')
	filetype = StringField(name='filetype')
	size = StringField(name='size')
	atime = StringField(name='atime')
	mtime = StringField(name='mtime')
	ctime = StringField(name='ctime')	


def init(Object):
	rows = yield from Object().createTable()
	if rows is not None:
		for row in rows:
			print(row)
def query(Object):
	rows = yield from Object().find()
	if rows is not None:
		for row in rows:
			print(row)
def start_server(func):
	loop = asyncio.get_event_loop()
	# tasks = [init(obj) for obj in [Comment]]
	tasks = [func(obj) for obj in [User, Blog, Comment, File]]
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()

if __name__ == '__main__':
	print(__doc__ % __author__)

	argv = sys.argv[1:]
	if not argv:
		logging.info('\nUsage: ./domain.py option\n\t0 - init\n\t1 - query')
		exit(0)
	if argv[0] == '0':
		start_server(init)
	elif argv[0] == '1':
		start_server(query)