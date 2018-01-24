#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*      Core      *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')

import functools, inspect, asyncio, os, json, time, hashlib, sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from aiohttp import web
from apis import APIError
from domain import User

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf.config import configs

COOKIE_KEY = configs.session.secret
_COOKIE_NAME = configs.session.cookie

def get(path):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = 'GET'
		wrapper.__route__ = path
		return wrapper
	return decorator

def post(path):
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = 'POST'
		wrapper.__route__ = path
		return wrapper
	return decorator

def get_request_kw_args(func):
	args = []
	params = inspect.signature(func).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
			logging.info('%s request_kw_args: %s ==> %s' % (func.__name__, name, param))
			args.append(name)
	return tuple(args)
	
def get_name_kw_args(func):
	args = []
	params = inspect.signature(func).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			logging.info('%s request_kw_args: %s ==> %s' % (func.__name__, name, param))
			args.append(name)
	return tuple(args)

def has_name_kw_args(func):
	params = inspect.signature(func).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			return True

def has_var_kw_args(func):
	params = inspect.signature(func).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.VAR_KEYWORD:
			return True

def has_request_args(func):
	sig = inspect.signature(func)
	params = sig.parameters
	found = False
	for name, param in params.items():
		if name == 'request':
			found = True
			continue
#		if found and (param != inspect.Parameter.VAR_POSITIONAL and param != inspect.Parameter.KEYWORD_ONLY and param != inspect.Parameter.VAR_KEYWORD):
#			raise ValueError('request parameter must be the last name parameter in function: %s%s' % (func.__name__, str(sig)))
	return found

class RequestHandler(object):
	def __init__(self, app, func):
		self._app = app
		self._func = func
		self._request_kw_args = get_request_kw_args(func)
		self._name_kw_args = get_name_kw_args(func)
		self._has_name_kw_args = has_name_kw_args(func)
		self._has_var_kw_args = has_var_kw_args(func)
		self._has_request_args = has_request_args(func)

	@asyncio.coroutine
	def __call__(self, request):
		kw = None
		if self._has_var_kw_args or self._has_name_kw_args or self._request_kw_args:
			if request.method == 'POST':
				if not request.content_type:
					return web.HTTPBadRequest(reason='Miss Cobtent-Type')
				content_type = request.content_type.lower()
				if content_type.startswith('application/json'):
					params = yield from request.json()
					if not isinstance(params, dict):
						return web.HTTPBadRequest(reason='JSON body must be object.')
					kw = params
				elif content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith('application/form-data'):
					params = request.post()
					kw = dict(**params)
				else:
					return web.HTTPBadRequest(reason='Unsupported Content-Type: %s' % request.content_types)
			
			if request.method == 'GET':
				qs = request.query_string
				if qs:
					kw = dict()
					for k, v in parse.parse_qs(qs, True).items():
						kw[k] = v[0]
		
		if kw is None:
			kw = dict(**request.match_info)
		else:
			if not self._has_var_kw_args and self._name_kw_args:
				copy = dict()
				for name in self._name_kw_args:
					if name in kw:
						copy[name] = kw[name]
				kw = copy
			for k, v in request.match_info.items():
				if k in kw:
					logging.info('request args in kw args: %s' % k)
				kw[k] = v
		
		if self._has_request_args:
			kw['request'] = request
		
		if self._request_kw_args:
			for name in self._request_kw_args:
				if name not in kw:
					return web.HTTPBadRequest(reason='Miss arg: %s' % name)
		logging.info('%s call with args: %s' % (self._func.__name__, str(kw)))
		try:
			rep = yield from self._func(**kw)
			return rep
		except APIError as e:
			logging.exception(e)
			return dict(error = e.error, data = e.data, message = e.message)

def add_route(app, fn):
	method = getattr(fn, '__method__', None)
	path = getattr(fn, '__route__', None)
	if path is None or method is None:
		raise ValueError('@get or @post not defined in %s' % str(fn))
	if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
		fn = asyncio.coroutine(fn)
	logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
	app.router.add_route(method, path, RequestHandler(app, fn))

def add_routes(app, module_name):
	n = module_name.rfind('.')
	if n == -1:
		mod = __import__(module_name, globals(), locals())
	else:
		name = module_name[n + 1:]
		mod = getattr(__import__(module_name[:n], globals(), locals()), name)
	for attr in dir(mod):
		if attr.startswith('_'):
			continue
		fn = getattr(mod, attr)
		if callable(fn):
			method = getattr(fn, '__method__', None)
			path = getattr(fn, '__route__', None)
			if method and path:
				add_route(app, fn)

def init_jinjia2(app, **kw):
	logging.info('init jinjia2 ...')
	options = dict(
		autoescape = kw.get('autoescape', True),
		block_start_string = kw.get('block_start_string', '{%'),
		block_end_string = kw.get('block_end_string', '%}'),
		variable_start_string = kw.get('variable_start_string', '{{'),
		variable_end_string = kw.get('variable_end_string', '}}'),
		auto_reload = kw.get('auto_reload', True)
	)
	path = kw.get('path', None)
	if path is None:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	logging.info('set jinjia2 template path: %s' % path)
	env = Environment(loader=FileSystemLoader(path), **options)
	filters = kw.get('filters', None)
	if filters is not None:
		for name, f in filters.items():
			env.filters[name] = f
	app['__templating__'] = env

@asyncio.coroutine
def logger_factory(app, handler):
	@asyncio.coroutine
	def logger(request):
		logging.info('Request: %s %s' % (request.method, request.path))
		logging.info('handler: %s' % handler.__name__)
		return (yield from handler(request))
	
	return logger

@asyncio.coroutine
def response_factory(app, handler):
	@asyncio.coroutine
	def response(request):
		logging.info('Response handler: %s ...' % handler.__name__)
		rep = yield from handler(request)
		logging.info('rep: %s' % str(rep))
		if isinstance(rep, web.StreamResponse):
			return rep
		if isinstance(rep, bytes):
			rep = web.Response(body=rep)
			rep.content_type = 'application/octet-stream'
			return rep
		if isinstance(rep, str):
			if rep.startswith('redirect:'):
				return web.HTTPFound(rep[9:])
			rep = web.Response(body=rep.encode('utf-8'))
			rep.content_type = 'text/html;charset=utf-8'
			return rep
		if isinstance(rep, dict):
			template = rep.get('__template__')
			if template is None:
				rep['__user__'] = request.__user__
				rep = web.Response(body=json.dumps(rep, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
				rep.content_type = 'text/json;charset=utf-8'
				return rep
			else:
				rep['__user__'] = request.__user__
				rep = web.Response(body=app['__templating__'].get_template(template).render(**rep).encode('utf-8'))
				rep.content_type = ' text/html;charset=utf-8'
				return rep
		if isinstance(rep, int) and rep >= 100 and rep < 600:
			return web.Response(rep)
		if isinstance(rep, tuple) and len(rep) == 2:
			t, m = rep
			if isinstance(t, int) and t >=100 and t < 600:
				return web.Response(t, str(m))
				
		rep = web.Response(str(rep).encode('utf-8'))
		rep.content_type = 'text/html;charset=utf-8'
		return rep
	
	return response
	
def datetime_filter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return '1分钟前'
	if delta < 3600:
		return '%s分钟前' % (delta // 60)
	if delta < 86400:
		return '%s小时前' % (delta // 3600)
	if delta < 604800:
		return '%s天前' % (delta // 86400)
	dt = datetime.fromtimestamp(t)
	return '%s年%s月%s日' % (dt.year, dt.month, dt.day)

def add_static(app):
	path = os.path.join(os.path.dirname(__file__), 'static')
	app.router.add_static('/static/', path)
	logging.info('add static %s => %s' % ('/static/', path))

def user2cookie(user, max_age):
	duration = str(int(time.time() + max_age))
	cookies = '%s-%s-%s-%s' % (user.id, user.password, duration, COOKIE_KEY)
	zip_cookie = [user.id, duration, hashlib.sha1(cookies.encode('utf-8')).hexdigest()]

	return '-'.join(map(str, zip_cookie))

def cookie2user(zip_cookie):
	if not zip_cookie:
		return None
	try:
		unzip_cookie = zip_cookie.split('-')
		if len(unzip_cookie) != 3:
			return None
		uid, duration, sha1 = unzip_cookie
		if int(duration) < time.time():
			return None
		users = (yield from User(id = uid).find())['data']
		user = users[0]
		if user is None:
			return None
		cookies = '%s-%s-%s-%s' % (user.id, user.password, duration, COOKIE_KEY)
		if sha1 != hashlib.sha1(cookies.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user.password = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None

@asyncio.coroutine
def auth_factory(app, handler):
	@asyncio.coroutine
	def auth(request):
		logging.info('check user: %s => %s' % (request.method, request.path))
		request.__user__ = None
		cookies = request.cookies.get(_COOKIE_NAME)
		if cookies:
			user = yield from cookie2user(cookies)
			if user:
				logging.info('set current user: %s' % user.email)
				request.__user__ = user
		if request.path.startswith('/manage/') and (request.__user__ is None or request.__user__.admin == '0'):
			return web.HTTPFound('/login')
		return (yield from handler(request))
	return auth	

if __name__ == '__main__':
	print(__doc__ % __author__)
	
