#!/usr/bin/env python3

class Flag() :
	def __init__(self, ** arg_nam) :
		self.data = { i : True if arg_nam[i] else False for i in arg_nam }
		
	def __getitem__(self, key) :
		try :
			return self.data[key]
		except KeyError :
			return None
			
	def __setitem__(self, key, value) :
		if value is None and key in self.data :
			del self.data[key]
		else :
			self.data[key] = (True if value else False)
		
	def __iter__(self) :
		for key in sorted(self.data) :
			yield key, self.data[key]
			
	def add(self, key, value=True) :
		self[key] = value
		
	def parse(self, line) :
		if line[0] == '!' :
			self.data[line[1:]] = False
		else :
			self.data[line] = True
		
	def remove(self, key) :
		if key in self.data :
			del self.data[key]
			
	def __repr__(self) :
		arg = ', '.join("{0}={1}".format(key, repr(value)) for key, value in self.data.items())
		return "{0}({1})".format(self.__class__.__name__, arg)
