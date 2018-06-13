#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*     Config     *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'
#默认的配置
configs = {
	'db': {
		'name': 'test.db',
		'conn': 100
	},
	'host': '0.0.0.0',
	'port': 8080,
	'session': {
		'secret': 'Shadaileng',
		'cookie': 'shadaileng'
	}
}
#Dict对象，配置[属性] => 对象.属性
class Dict(dict):
	"""docstring for Dict"""
	def __init__(self, name=(), values=(), **kw):
		super(Dict, self).__init__(**kw)
		for k, v in zip(name, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError as e:
			raise AttributeError('Dict object has no attribute %s' % key)

	def __setattr__(self, key, value):
		self[key] = value
#合并默认配置和覆盖配置
def merge(default, override):
	r = default

	for k, v in override.items():
		r[k] = (merge(default[k], v) if isinstance(v, dict) else v) if k in default.keys() else v
		# if k in default.keys():
		# 	if isinstance(v, dict):
		# 		r[k] = merge(default[k], v)
		# 	else:
		# 		r[k] = v
		# else:
		# 	r[k] = v

	return r
#将dict转化为Dict类
def toDict(d):
	D = Dict()
	for k, v in d.items():
		D[k] = toDict(v) if isinstance(v, dict) else v

	return D

try:
	import sys, os
	from conf.config_override import configs as config_override
	configs = merge(configs, config_override)
except Exception as e:
	print('error: %s' % e)
#最终的配置
configs = toDict(configs)

if __name__ == '__main__':
	print(__doc__ % __author__)

	print(configs)