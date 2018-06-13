#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*       API      *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'
import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')
import sys, os, asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.config import configs
from tools import loadResource

from domain import File

def initFile(flag):
	# 清空File表
	if(flag == '0'):
		res = yield from File().delete()
		logging.info('delete: %s' % res)
	# 导入File数据
	path = ''
	if 'win' in sys.platform:
		path = configs.dev.win.datapath.file
	elif 'linux' in sys.platform:
		path = configs.dev.linux.datapath.file
	if path != '':
		files = loadResource(path)
		for file in files:
			res = yield from File(**file).save()
			print('res: %s' % res)

def start_server(func, arg):
	loop = asyncio.get_event_loop()
	tasks = [func(arg)]
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()

if __name__ == '__main__':
	argv = sys.argv[1:]
	logging.info('argv: %s' % argv)
	logging.info('platform: %s' % sys.platform)
	if not argv and len(argv) < 2:
		logging.info('\nUsage: ./init.py option \n\t0 - file')
		exit(0)
	if argv[0] == '0':
		start_server(initFile, argv[1])