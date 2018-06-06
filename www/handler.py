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

from aiohttp import web
from datetime import datetime
from core import get, post, user2cookie, cookie2user
from domain import User, Blog, Comment, File, next_id
from apis import APIError, APIValueError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.config import configs

_COOKIE_NAME = configs.session.cookie

_RE_EMAIL = re.compile(r'^[0-9a-z\-\_\.]+\@[0-9a-z\-\_]+(\.[0-9a-z\-\_]+){1,4}$')

@get('/test')
def index(request):
	return {
		'__template__': 'users.html'
	}

@get('/')
def api_get_blogs(request):
	
	blogs = (yield from Blog().find())['data']
	for blog in blogs:
		blog.createtime = datetime.strptime(blog.createtime, '%Y-%m-%d %H:%M:%S,%f').timestamp()
		user = (yield from User(id = blog.userid).find())['data'][0]
		blog.author = user

	return {
		'__template__': 'blogs.html',
		'blogs': blogs
	}

@get('/api/users/{page}/{pagesize}')
def api_get_users(*, page='0',pagesize = '0'):
	users = (yield from User().find(limit=int(pagesize), offset=int(pagesize) * int(page)))['data']
	for user in users:
		logging.info('user: %s' % user)

	return dict(users=users)

@get('/register')
def redirect_regiest(request):
	return {
		'__template__': 'user_register.html',
		'action': '/api/user/register'
	}

@post('/api/user/register')
def api_user_register(*, name, password, email):
	if not name or not name.strip():
		raise APIValueError('name', 'name is Null')
	if not password or not password.strip():
		raise APIValueError('password', 'password is Null')
	if not email or not email.strip():
		raise APIValueError('email', 'email is Null')
	if not _RE_EMAIL.match(email):
		raise APIValueError('email: %s' % email, 'email is no format')
	users = (yield from User(email=email).find())['data']
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
		'__template__': 'user_login.html',
		'action': '/api/user/authenticate'
	}

@post('/api/user/authenticate')
def api_user_authenticate(*, email, password):
	if not email or not email.strip():
		raise APIValueError('email', 'email is Null')
	if not _RE_EMAIL.match(email):
		raise APIValueError('email', 'email is not format')
	if not password or not password.strip():
		raise APIValueError('password', 'password is Null')
	users = (yield from User(email=email).find())['data']
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

@get('/manage/blog/edit/{id}')
def redirect_blog_edit(request, *, id):
	return {
		'__template__': 'blog_edit.html',
		'id': id,
		'action': '/api/blog'
	}

@post('/api/blogs')
def api_blog_edit(request, *, id, name, summary, content):
	if request.__user__ is None:
		raise APIError('blog', 'edit', 'edit blog before login')
	if not name or not name.strip():
		raise APIValueError('name', 'name is Null')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary is Null')
	if not content or not content.strip():
		raise APIValueError('content', 'content is Null')

	blog = Blog(name=name, userid=request.__user__.id, summary=summary, content=content, updatetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'))
	if id:
		blog.id = id
		res = yield from blog.update()
	else:
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

@get('/manage/blogs')
def redirect_blog_list(request):
	return {
		'__template__': 'blog_list.html',
		'action': '/api/blogs'
	}

@get('/api/blogs')
def api_blog_list(*, page='0'):
	try:
		if int(page) < 0:
			page = 0
	except Exception as e:
		logging.exception(e)
		page = 0
	page = int(page)
	pagesize = 5
	data = (yield from Blog().find(index=page, limit=pagesize))
	blogs = data['data']
	info = data['info']
	for blog in blogs:
#		blog.createtime = datetime.strptime(blog.createtime, '%Y-%m-%d %H:%M:%S,%f').timestamp()
		user = (yield from User(id = blog.userid).find())['data'][0]
		blog.author = user

	return {"blogs":blogs, "page":info}

@get('/manage/blog/detail/{id}')
def redirect_blog_detail(*, id):
	return {
		'__template__': 'blog_detail.html',
		'action': '/api/blog/' + id
	}

@get('/api/blog/{id}')
def api_blog_detail(*, id=0):
	blogs = (yield from Blog(id=id).find())['data']
	for blog in blogs:
#		blog.createtime = datetime.strptime(blog.createtime, '%Y-%m-%d %H:%M:%S,%f').timestamp()
		user = (yield from User(id = blog.userid).find())['data'][0]
		blog.author = user
	return {'blog': blogs[0]}

@get('/api/images')
def redirect_image_list(request):
	return {
		'__template__': 'images.html',
<<<<<<< HEAD
		'action': '/api/load/images',
=======
		'action': '/api/load/images/0',
		'page_index': 0
>>>>>>> b1807042293fce5cb678bcac68ef6b7cafb4880e
	}

@get('/api/load/images/{page}')
def api_images(*, page='0'):
	try:
		if int(page) < 0:
			page = 0
	except Exception as e:
		logging.exception(e)
		page = 0
	page = int(page)
	pagesize = 10
	data = (yield from File().find(index=page, limit=pagesize))
	images = list({'hashpath': image.hashpath, 'name': image.name} for image in data['data'])
	info = data['info']
	print('info: %s' % info)

	return {"images":images, "page":info}

@get('/api/file/{id}')
def api_file(request, *, id):
	data = (yield from File(hashpath=id).find())['data']
	path = r'F:\qipf\bak\img\leimu.jpg'
	print('data: %s' % data)
	if data is not None and len(data) > 0:
		file = data[0]
		path = file.path
	rep = web.FileResponse(path)  
	rep.enable_compression()  
	return rep  


if __name__ == '__main__':
	print(__doc__ % __author__)
	
