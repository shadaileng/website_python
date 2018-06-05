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

def query(sql):
#	res = yield from execute('create table user(id number(50) primary key, name varchar(50), password varchar(50), email varchar(50), admin number(1), image varchar(500), create_time varchar(50))')
#	
#	print('create user: %s' % res)
#	
#	res = yield from execute('create table blog(id number(50) primary key, user_id number(50), name varchar(50), summary varchar(50), content varchar(255), create_time varchar(50))')

#	print('create blog: %s' % res)
#	
#	res = yield from execute('create table comment(id number(50) primary key, user_id number(50), blog_id number(50), content varchar(255), create_time varchar(50))')
#	
#	print('create comment: %s' % res)
#	
#	res = yield from execute('create table file(hashpath varchar(100), path varchar(100), filetype varchar(50), size number(20), atime varchar(50), mtime varchar(50), ctime varchar(50))')
#	
#	print('create comment: %s' % res)
	
	res = yield from select(sql, ())
	print(res)
	for row in res:
		print(row)

def execu(sql):
	res = yield from execute(sql, ())
	print('execute res: %s' % res)

def start_server(func, sql):
	loop = asyncio.get_event_loop()
	tasks = [func(sql) for sql in [sql]]
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()

if __name__ == '__main__':
	print(__doc__ % __author__)
	argv = sys.argv[1:]
	if not argv or len(argv) < 2:
		logging.info('\nUsage: ./db_sqlite.py option sql\n\t0 - execu\n\t1 - query')
		exit(0)
	if argv[0] == '0':
		start_server(execu, argv[1])
	elif argv[0] == '1':
		start_server(query, argv[1])