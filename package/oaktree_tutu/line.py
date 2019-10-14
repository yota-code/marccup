#!/usr/bin/env python3

class Line() :
	def __init__(self, pos=None, nam=None, flag=None, style=None) :
		self.pos = list(pos) if pos is not None else list()
		self.nam = dict(nam) if nam is not None else dict()
		self.flag = set(flag) if flag is not None else set()
		self.style = set(style) if style is not None else set()
		
	def __getitem__(self, key) :
		if isinstance(key, str) :
			return self.nam[key]
		elif isinstance(key, int) :
			return self.pos[key]
		else :
			raise KeyError("{0} is not a valid key".format(type(key)))
			
	def __setitem__(self, key, value) :
		if key is None :
			self.pos.append(value)
		elif isinstance(key, str) :
			self.nam[key] = value
		elif isinstance(key, int) :
			self.pos[key] = value
			
	def __contains__(self, key) :
		try :
			self[key]
			return True
		except (IndexError, KeyError) :
			return False
			
	def is_empty(self) :
		return len(self.pos) + len(self.nam) + len(self.flag) + len(self.style) == 0
		
	def clear(self) :
		self.pos.clear()
		self.nam.clear()
		self.flag.clear()
		self.style.clear()
		return self
		
