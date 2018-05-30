#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*       ORM      *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import logging; logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s line:%(lineno)d %(filename)s %(funcName)s >>> %(message)s')

import asyncio
from apis import APIValueError
from db_sqlite import select, execute

class Field(object):
	def __init__(self, name, column_type, primary_key = False, default=None):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default
	def __str__(self):
		return '<%s: %s, %s %s>' % (self.__class__.__name__, self.column_type, self.name, self.primary_key)

class IntegeField(Field):
	def __init__(self, name, column_type='Number(50)', primary_key = False, default=None):
		super(IntegeField, self).__init__(name, column_type, primary_key, default)

class StringField(Field):
	def __init__(self, name, column_type='varchar(50)', primary_key = False, default=None):
		super(StringField, self).__init__(name, column_type, primary_key, default)

class ModelMetaclass(type):
	def __new__(cls, name, bases, attrs):
		if name == 'Model':
			return type.__new__(cls, name, bases, attrs)
		
		logging.info('found model: %s' % name)
		
		mappings = dict()
		fields = []
		primary_key = None
		
		for k, v in attrs.items():
			if isinstance(v, Field):
				logging.info('  found mapping: %s ==> %s' % (k, v))
				mappings[k] = v
				if v.primary_key:
					if primary_key:
						raise APIValueError(k, 'already has primary_key %s' % primary_key)
					primary_key = k
				fields.append(k)
		if primary_key is None:
			raise APIError('', '', 'not found primary_key')
		for k in mappings.keys():
			attrs.pop(k)
		attrs['__mappings__'] = mappings
		attrs['__primary_key__'] = primary_key
		attrs['__fields__'] = fields
		attrs['__table__'] = name.upper()
		return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaclass):
	def __init__(self, **kw):
		super(Model, self).__init__(**kw)
	
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError('Model object has no attribute %s' % key)
	
	def __setattr__(self, key, val):
		self[key] = val
	
	def getValue(self, key):
		return getattr(self, key, None)
	
	def getValueDefault(self, key):
		value = self.getValue(key)
		if value is None:
			field = self.__mappings__[key]
			if field.default is not None:
				value = field.default() if callable(field.default) else field.default
				logging.info('field %s use default value: %s' % (key, value))
				setattr(self, key, value)
		return value
	
	def rows2mapping(self, rows):
		mappings = []
		fields = list(self.__fields__)
		logging.info('fields: %s' % fields)
		logging.info('rows: %s' % rows)
		for row in rows:
			mappings.append(dict(zip(fields, row)))
			# logging.info(type(row))
			# mapping = {}
			# for index, value in enumerate(fields):
			# 	mapping[value] = row[index]
			# mappings.append(mapping)
		logging.info('mappings: %s' % mappings)
		return mappings
	
	@asyncio.coroutine
	def save(self):
		logging.info('=======================save=======================');
		params = []
		args = []
		for field in self.__fields__:
			params.append('?')
			args.append(self.getValueDefault(field))
		sql = 'insert into %s(%s) values(%s)' % (self.__table__, ','.join(list(map(lambda x: x.upper(), self.__fields__))), ','.join(params))
		logging.info('SQL : %s' % sql)
		logging.info('ARGS: %s' % args)
		res = yield from execute(sql, args)
		logging.info('save: %s' % res)
		if res == 0:
			logging.info('insert 0 row')
		logging.info('===============================================');
		return res

	@asyncio.coroutine
	def delete(self):
		logging.info('=======================delete=====================');
		params = []
		args = []
		for field in self.__fields__:
			value = self.getValue(field)
			if value is None:
				continue
			params.append('%s = ?' % field)
			args.append(value)
		sql = 'delete from %s where %s' % (self.__table__, ','.join(params))
		logging.info('SQL : %s' % sql)
		logging.info('ARGS: %s' % args)
		res = yield from execute(sql, args)
		logging.info('delete: %s' % res)
		if res == 0:
			logging.info('delete 0 row')
		logging.info('===============================================');
		return res

	@asyncio.coroutine
	def update(self):
		logging.info('=====================update=====================');
		params = []
		args = []
		logging.info(self.getValue(self.__primary_key__))
		if self.getValue(self.__primary_key__) is None:
			raise APIValueError(self.__primary_key__, 'field %s can not be null' % self.__primary_key__)
		for field in self.__fields__:
			value = self.getValue(field)
			if value is None or field == self.__primary_key__:
				continue
			params.append('%s = ?' % field)
			args.append(value)
		args.append(self.getValue(self.__primary_key__))
		sql = 'update %s set %s where %s' % (self.__table__, ','.join(params), '%s = ?' % self.__primary_key__)
		logging.info('SQL : %s' % sql)
		logging.info('ARGS: %s' % args)
		res = yield from execute(sql, args)
		logging.info('update: %s' % res)
		if res == 0:
			logging.info('update 0 row')
		logging.info('===============================================');
		return res

	@asyncio.coroutine
	def find(self, index=0, limit=0):
		logging.info('======================find========================');
		params = ['1 = 1']
		args = []
		for field in self.__fields__:
			value = self.getValue(field)
			if value is None:
				continue
			params.append('%s = ?' % field)
			args.append(value)
		sql = 'select count(%s) _num_ from %s where %s' % (self.__primary_key__, self.__table__, ' and '.join(params))
		logging.info('sql: %s' % sql)
		logging.info('ARG: %s' % args)
		count = yield from select(sql, args)
		logging.info('find count: %s' % count)
		item_count = 0
		if count is not None:
			if limit <= 0:
				limit = count[0][0]
				index = 0
			item_count = count[0][0]
		else:
			limit = 0
			index = 0

		sql = 'select %s from %s where %s limit %d offset %s' % (','.join(list(map(lambda x: x.upper(), self.__fields__))), self.__table__, ' and '.join(params), limit, index * limit)
		logging.info('SQL: %s' % sql)
		logging.info('ARG: %s' % args)
		res = yield from select(sql, args)
		logging.info('find: %s' % res)
		if res is None:
			logging.info('find 0 row')
		rows = self.rows2mapping(res)
		logging.info('rows: %s' % rows)
		page_count = 0 if limit == 0 else (item_count // limit + 1) if (item_count % limit) else (item_count // limit)
		returnObj = {
						'info': {
							'has_next': False if index == page_count else True,
							'has_previous': False if index == 0 else True,
							'page_index': index,
							'page_count': page_count,
							'item_count': item_count
						},
						'data': [Model(** row) for row in rows]
					}
		logging.info("return: %s" % returnObj)
		logging.info('===============================================')
		return returnObj

	@asyncio.coroutine
	def findCount(self):
		logging.info('====================findCount=====================')
		params = ['1 = 1']
		args = []
		for field in self.__fields__:
			value = self.getValue(field)
			if value is None:
				continue
			params.append('%s = ?' % field)
			args.append(value)
		sql = 'select count(%s) _num_ from %s where %s' % (self.__primary_key__, self.__table__, ' and '.join(params))

		logging.info('SQL: %s' % sql)
		logging.info('ARG: %s' % args)
		count = yield from select(sql, args)
		logging.info('count: %s' % count)
		if count is None:
			count = 0
		else:
			count = count[0][0]
		logging.info('===============================================')
		return count;
	
if __name__ == '__main__':
	print(__doc__ % __author__)
