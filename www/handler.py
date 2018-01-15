#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*     Handles    *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'
import time

from core import get, post
from aiohttp import web
from domain import User, Blog, Comment


@get('/')
def index(request):
	return web.Response(body=b'<h1>Index</h1>', content_type='text/html')

@get('/blogs')
def api_get_blogs(request):
	summary = '只是一条日志，我也不知道要写些什么'
	blogs = [
		Blog(id='1', name='富强', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='民主', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='文明', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='和谐', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='自由', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='平等', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='公正', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='法治', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='爱国', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='敬业', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='诚实', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id='1', name='友善', user_id=1, summary=summary, content='略', create_time=time.time()-120)
	]
	print(blogs)
	return {
		'__template__': 'blogs.html',
		'blogs': blogs
	}

@get('/users')
def api_get_users(request):
	users = yield from User().find()
	return {
		'__template__': 'users.html',
		'users': users
	}


if __name__ == '__main__':
	print(__doc__ % __author__)
	
