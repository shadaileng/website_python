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

import functools, inspect, asyncio, os, json, time
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from aiohttp import web
from apis import APIError

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
		wrapper.path = path
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
	sign = inspect.signature(func)
	params = sign.parameters
	found = False
	for name, param in params.items():
		if name == 'request':
			found = True
			continue
		if found and (param != inspect.Parameter.VAR_POSITIONAL and param != inspect.Parameter.KEYWORD_ONLY and param != inspect.Parameter.VAR_KEYWORD):
			raise ValueError('request parameter must be the last name parameter in function: %s%s' % (func.__name__, str(sig)))
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
	
	def __call__(self, request):
		kw = None
		if self._has_var_kw_args or self._has_name_kw_args or self._request_kw_args:
			if request.method == 'POST':
				if not request.content_type:
					return HTTPBadResponse('Miss Cobtent-Type')
				content_type = request.content_type.lower()
				if content_type.startswith('application/json'):
					params = request.json()
					if not isinstance(params, dict):
						return HTTPBadResponse('JSON body must be object.')
					kw = params
				elif content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith('application/form-data'):
					params = request.post()
					kw = dict(**params)
				else:
					return HTTPBadResponse('Unsupported content_type: %s' % content_type)
			
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
					return HTTPBadResponse('Miss arg: %s' % name)
		logging.info('%s call with args: %s' % (self._func.__name__, str(kw)))
		try:
			rep = yield from self._func(**kw)
			return rep
		except APIError as e:
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
		return (yield from handler(request))
	
	return logger

@asyncio.coroutine
def response_factory(app, handler):
	@asyncio.coroutine
	def response(request):
		logging.info('Response handler ...')
		rep = yield from handler(request)
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
				rep = web.Response(body=json.dumps(rep, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
				rep.content_type = 'text/json;charset=utf-8'
				return rep
			else:
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

if __name__ == '__main__':
	print(__doc__ % __author__)
	
