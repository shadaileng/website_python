#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	********************
	*       Tools      *
	********************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')
import hashlib, os, filetype, sys, asyncio
from datetime import datetime
from domain import File

def loadResource(path):
	files = []
	def traversal(path, indent=0):
		if path is None or os.path.isfile(path):
			return
		for file in os.listdir(path):
			path_ = os.path.join(path, file)
			if os.path.exists(path_):
				if os.path.isfile(path_):
					stat = os.stat(path_)
					corvertime = lambda t: datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
					fileObj = {'name': file, 'hashpath': hashlib.sha1(path_.encode('utf-8')).hexdigest(),'path': path_, 'filetype': filetype.guess(path_).mime if filetype.guess(path_) else path_[path_.rfind('.') + 1 :], 'size': stat[-4], 'atime': corvertime(stat[-3]), 'mtime': corvertime(stat[-2]), 'ctime': corvertime(stat[-1])}
					files.append(fileObj)
					print('%s/*%s' % (' ' * indent, file))
				else:
					print('%s|>%s' % (' ' * indent, file), os.stat(path_)[-3:])
					traversal(path_, indent + 1)
	traversal(path)
	return files

def record(path):
	print(path)
	files = loadResource(path)
	for file in files:
		res = yield from File(**file).save()
		print('res: %s' % res)

def start_server(func, argv):
	loop = asyncio.get_event_loop()
	tasks = [func(argv)]
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()

if __name__ == '__main__':
	argv = sys.argv[1:]
	if not argv or len(argv) < 2:
		logging.info('\nUsage: ./tools.py option path\n\t0 - record')
		exit(0)
	if argv[0] == '0':
		start_server(record, argv[1])
	if argv[0] == '1':
		start_server(test, argv[1])