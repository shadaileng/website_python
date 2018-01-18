#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*     Handles    *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'
import time, re, json, sys, os, hashlib
import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')

from core import get, post, user2cookie, cookie2user
from aiohttp import web
from domain import User, Blog, Comment, next_id
from apis import APIValueError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.config import configs

_COOKIE_NAME = configs.session.cookie

_RE_EMAIL = re.compile(r'^[0-9a-z\-\_\.]+\@[0-9a-z\-\_]+(\.[0-9a-z\-\_]+){1,4}$')

@get('/test')
def index(request):
	return web.Response(body=b'<h1>test</h1>', content_type='text/html')

@get('/')
def api_get_blogs(request):
	summary = '只是一条日志，我也不知道要写些什么'
	blogs = [
		Blog(id = '1', name='富强', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '2', name='民主', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '3', name='文明', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '4', name='和谐', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '5', name='自由', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '6', name='平等', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '7', name='公正', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '8', name='法治', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '9', name='爱国', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '10', name='敬业', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '11', name='诚实', user_id=1, summary=summary, content='略', create_time=time.time()-120),
		Blog(id = '12', name='友善', user_id=1, summary=summary, content='略', create_time=time.time()-120)
	]
#	print(blogs)
	return {
		'__template__': 'blogs.html',
		'blogs': blogs
	}

@get('/api/users/{page}/{pagesize}')
def api_get_users(*, page='0',pagesize = '3'):
	users = yield from User().find(limit=int(pagesize), offset=int(pagesize) * int(page))
	for user in users:
		logging.info('user: %s' % user)

	return dict(users=users)

@get('/register')
def redirect_regiest(request):
	return {
		'__template__': 'register.html'
	}

@post('/api/register')
def api_register_user(*, name, password, email):
	if not name or not name.strip():
		raise APIValueError('name', 'name is Null')
	if not password or not password.strip():
		raise APIValueError('password', 'password is Null')
	if not email or not email.strip():
		raise APIValueError('email', 'email is Null')
	if not _RE_EMAIL.match(email):
		raise APIValueError('email: %s' % email, 'email is no format')
	users = yield from User(email=email).find()
	if len(users) > 0:
		raise APIValueError('email', 'email: %s is already in use' % email)
	uid = next_id()
	sha1_password = '%s:%s' % (uid, password)
	user = User(id = uid, name = name, password = hashlib.sha1(sha1_password.encode('utf-8')).hexdigest() , email = email, image='./res/tumble.png')
	res = yield from user.save()
	rep = web.Response()
	rep.content_type = 'application/json'
	if res == 1:
		logging.info('save user sucessed')
		rep.set_cookie(_COOKIE_NAME, user2cookie(user, 86400), max_age = 86400, httponly=True)
		user.password = '******'
		rep.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	else:
		logging.error('user save error')
		raise APIError('register', 'save', 'register failed')

	return rep

@get('/login')
def redirect_login(request):
	return {
		'__template__': 'login.html'
	}

@post('/api/authenticate')
def api_authenticate_user(*, email, password):
	if not email or not email.strip():
		raise APIValueError('email', 'email is Null')
	if not _RE_EMAIL.match(email):
		raise APIValueError('email', 'email is not format')
	if not password or not password.strip():
		raise APIValueError('password', 'password is Null')
	users = yield from User(email=email).find()
	if len(users) == 0:
		raise APIValueError('email', 'email is not in use')
	user = users[0]
	sha1_password = '%s:%s' % (user.id, password)
	if hashlib.sha1(sha1_password.encode('utf-8')).hexdigest() != user.password:
		raise APIValueError('password', 'password is error')

	rep = web.Response()
	rep.content_type = 'application/json'
	rep.set_cookie(_COOKIE_NAME, user2cookie(user, 86400), max_age = 86400, httponly=True)
	user.password = '******'
	rep.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return rep

@get('/logout')
def redirect_logout(request):
	referer = request.headers.get('Referer')
	rep = web.HTTPFound(referer or '/')
	rep.set_cookie(_COOKIE_NAME, '-delete-', max_age=0, httponly=True)
	logging.info('user logout')

	return rep

@get('/manage/blog/edit')
def redirect_edit_blog(request):
	return {
		'__template__': 'edit_blog.html',
		'id': '',
		'action': '/api/blogs'
	}

@post('/api/blogs')
def api_edit_blog(request, *, name, summary, content):
	if request.__user__ is None:
		raise APIError('blog', 'edit', 'edit blog before login')
	if not name or not name.strip():
		raise APIValueError('name', 'name is Null')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary is Null')
	if not content or not content.strip():
		raise APIValueError('content', 'content is Null')

	blog = Blog(name=name, user_id=request.__user__.id, summary=summary, content=content)

	res = yield from blog.save()

	rep = web.Response()
	rep.content_type = 'application/json'
	if res == 1:
		logging.info('save blog sucessed')
		rep.body = json.dumps(blog, ensure_ascii=False).encode('utf-8')
	else:
		logging.info('save blog failed')
		raise APIError('edit blog', 'save', 'edit blog failed')

	return rep


if __name__ == '__main__':
	print(__doc__ % __author__)
	

