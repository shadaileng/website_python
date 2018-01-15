#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*       API      *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

class APIError(Exception):
	def __init__(self, error, data='', message=''):
		super(APIError, self).__init__(message)
		self.error = error
		self.data = data
		self.message = message

class APIValueError(APIError):
	def __init__(self, field, message=''):
		super(APIValueError, self).__init__('value: invalid', field, message)

class APIResourceNotFoundError(APIError):
	def __init__(self, field, message=''):
		super(APIResourceNotFoundError, self).__init__('value: notfound', field, message)

class APIPermissionError(APIError):
	def __init__(self, field, message=''):
		super(APIPermissionError, self).__init__('permission: forbidden', 'permission', message)

class APIConnectFullError(APIError):
	def __init__(self, field, message=''):
		super(APIConnectFullError, self).__init__('connect: full', field, message)

if __name__ == '__main__':
	print(__doc__ % __author__)
	
	print(APIError('error', 'data', 'message').args[0])
	print(APIError('error', 'data', 'message').error)
	print(APIError('error', 'data', 'message').data)
	print(APIError('error', 'data', 'message').message)
	print(APIConnectFullError('data', 'message'))
