#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*       DB       *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')
import sqlite3, asyncio, sys, os

from apis import APIConnectFullError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.config import configs

_coutnt = 0

DB_SRC = configs.db.name
MAX_CONN = configs.db.conn

def get_connect(db = DB_SRC, max = MAX_CONN):
	global _coutnt
	_coutnt += 1
	try:
		conn = sqlite3.connect(db)
#		if _coutnt <= max:
#			conn = sqlite3.connect(db)
#		else:
#			raise APIConnectFullError(db, '%s connection is full' % db)
	except Exception as e:
		logging.warning(e)
		conn = None
	if conn:
		logging.info('%s connect successed' % db)
	return conn

@asyncio.coroutine
def select(sql, args = (), size = None, db = DB_SRC):
	logging.info('%s %s' % (sql, args))
	try:
		with get_connect(db) as conn:
			cur = conn.cursor()
			cur.execute(sql, args or ())
			if size:
				rs = cur.fetchmany(size)
			else:
				rs = cur.fetchall()
	except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
		logging.error('Could not complete operation: %s' % e)
		rs = None
		cur = None
	finally:
		if cur is not None:
			cur.close()
	if rs is None:
		logging.warning('%s %s >>> find none' % (sql, args))
	else:
		logging.info('return result: %s' % len(rs))
	return rs

@asyncio.coroutine
def execute(sql, args = (), db = DB_SRC):
	logging.info('%s %s' % (sql, args))
	try:
		with get_connect(db) as conn:
			conn.execute(sql, args)
			change = conn.total_changes
	except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
		logging.error('Could not complete operation: %s' % e)
		change = 0
	logging.info('change rows: %d' % change)
	return change

def run():
#	rs = yield from select('select count(id) _num_ from User', ())
#	print(rs)
#	res = yield from execute('delete from user')
#	rs = yield from select('select * from User', ())
#	for r in rs:
#		print(r)
#	res = yield from execute('create table blog(id number(50) primary key, user_id number(50), name varchar(50), summary varchar(250), content varchar(2500), create_time varchar(50))')
#	print(res)
	
	res = yield from execute('create table user(id number(50) primary key, name varchar(50), password varchar(50), email varchar(50), admin number(1), image varchar(500), create_time varchar(50))')
	
	print('create user: %s' % res)
	
	res = yield from execute('create table blog(id number(50) primary key, user_id number(50), name varchar(50), summary varchar(50), content varchar(255), create_time varchar(50))')

	print('create blog: %s' % res)
	
	res = yield from execute('create table comment(id number(50) primary key, user_id number(50), blog_id number(50), content varchar(255), create_time varchar(50))')
	
	print('create comment: %s' % res)
	
	rs = yield from select('select * from blog', ())
	for r in rs:
		print(r)

def start_server():
	loop = asyncio.get_event_loop()
	loop.run_until_complete(run())
	loop.run_forever()

if __name__ == '__main__':
	print(__doc__ % __author__)
	
#	res = execute('create table user(id number(50) primary key, name varchar(50), password varchar(50), email varchar(50), admin number(1), image varchar(500), create_time varchar(50))')
	
#	res = execute('insert into user(id, name, password, email, admin, image, create_time) values(2, "chik", "123456", "qpf0510@qq.com", 0, "./res/tumblr.com", "2018-01-13 20:13:32")')
	
#	execute('update user set create_time=?, email=? where id = ?', ('2018-01-13 20:13:32', 'qpf0510@126.com', 2))

#	execute('insert into user(id, name, password, email, admin, image, create_time) values(?, ?, ?, ?, ?, ?, ?)', (3, "qpf", "123456", "qpf0510@163.com", 0, "./res/tumblr.com", "2018-01-13 20:23:32"))
	
#	rs = select('select * from user where id = ?', (3,))
	
	start_server()
	
#	rs = select('select * from user', ())
#	for r in rs:
#		print(r)
#	print('res: %s' % res)
	
'''
	for i in range(12):
		c = get_connect()
		print(c)
'''

