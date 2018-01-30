#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*    PyMonitor   *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='[Monitir] %(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')
import os, sys, time, subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyFileSyaytemEventHandler(FileSystemEventHandler):
	"""docstring for MyFileSyaytemEventHandler"""
	def __init__(self, fn):
		super(MyFileSyaytemEventHandler, self).__init__()
		self.restart = fn
	
	def on_any_event(self, event):
		if event.src_path.find('__pycache__') < 0:
			logging.info('python source file change: %s' % event.src_path)
			self.restart()

process = None
command = ['echo', 'ok']

def kill_process():
	global process
	if process:
		logging.info('kill process: %s' % process.pid)
		process.kill()
		process.wait()
		logging.info('process endede with code: %s' % process.returncode)
		process = None

def start_process():
	global process, command
	logging.info('start process: %s' % ' '.join(command))
	process = subprocess.Popen(command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

def restart_process():
	kill_process()
	start_process()

def start_watchdog(path, callback=None):
	observer = Observer()
	observer.schedule(MyFileSyaytemEventHandler(restart_process), path, recursive=True)
	observer.start()
	logging.info('watching directory: %s' % path)
	start_process()
	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

if __name__ == '__main__':
	print(__doc__ % __author__)

	argv = sys.argv[1:]
	if not argv:
		logging.info('Usage: ./pymonitor xx.py')
		exit(0)

	if argv[0] != 'python':
		argv.insert(0, 'python')

	command = argv
	path = os.path.abspath('./www')
	start_watchdog(path)