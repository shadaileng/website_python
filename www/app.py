#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*       App      *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')
import asyncio, sys, os

from aiohttp import web
from core import add_routes, init_jinjia2, logger_factory, response_factory, datetime_filter, add_static

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.config import configs

@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop, middlewares=[logger_factory, response_factory])
	init_jinjia2(app, filters=dict(datetime=datetime_filter))
	add_routes(app, 'handler')
	add_static(app)
	ip, port = (configs.host, configs.port)
	server = yield from loop.create_server(app.make_handler(), ip, port)
	logging.info('server start at http://%s:%s' % (ip, port))
	
	return server
def start_server():
	loop = asyncio.get_event_loop()
	loop.run_until_complete(init(loop))
	loop.run_forever()

if __name__ == '__main__':
	print(__doc__ % __author__)
	start_server()
#	print(configs.host)
