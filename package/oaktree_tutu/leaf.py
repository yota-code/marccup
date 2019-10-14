#!/usr/bin/env python3

import importlib
import ast
import inspect

import collections

import logging
logging.basicConfig(level=logging.DEBUG)
dbg = logging.debug

import oaktree

from oaktree.line import Line

_class_not_found = set()
def _debug_class_not_found(error, module_name, class_name) :
	u = (module_name, class_name)
	if u not in _class_not_found :
		dbg("{0}:{1}.{2}:class can not be found".format(error, module_name, class_name))
		_class_not_found.add(u)

def _walk_limit(start=None, stop=None, _depth=0) :
	return (
		(start is None or _depth >= start) and 
		(stop is None or _depth < stop) 
	)

class Leaf(Line) :
	
	_module_prefix = 'oak_'
	_class_suffix = 'Leaf'
	
	_loaded = True
	
	parent = None
	
	space = None
	tag = None
	ident = None
	
	_indent_mode = None
		
	def __init__(self, tag=None, ident=None, space=None, pos=None, nam=None, flag=None, style=None, indent_mode=None) :
		
		self._init_tag(tag)
		
		if ident is not None :
			self.ident = ident
		if space is not None :
			self.space = space
		
		Line.__init__(self, pos, nam, flag, style)
		
		if indent_mode is not None :
			self._indent_mode = indent_mode
				
		self.sub = list()
		
	def _init_tag(self, tag) :
		"""
		in this order of priority:
		 * the tag set by the __init__() call, if defined
		 * the tag set at the class level, if defined
		 * the tag guessed by the class name, if not empty
		 * __undefined___
		"""

		if tag is not None :
			self.tag = tag
		elif self.tag is not None :
			pass
		else :
			tag = self.__class__.__name__.replace(self._class_suffix, '')
			self.tag = tag if tag != '' else '__undefined__'
		
	@property
	def root(self) :
		root = self
		while root.parent is not None :
			root = root.parent
		return root
		
	@property
	def is_root(self) :
		return self.parent is None
		
	def down(self, tag, ident=None) :
		""" return the first leaf in sub, matching the tag, or the tag and the ident 
		TODO: replace all calls to pick_tag_ident et pick_tag par down
		"""
		for n_sub in self :
			if n_sub.tag == tag :
				if ident is None :
					return n_sub
				else :
					if n_sub.ident == ident :
						return n_sub
		raise KeyError("no ident={0}{1} in {2}".format(type(ident), ident,
			", ".join("{0}{1}".format(type(n.ident), repr(n.ident)) for n in self))
		)
		
	""" pick: return the first matching among direct children """
	def pick_tag_ident(self, tag, ident) :
		""" return the first matching leaf among direct sub-leaves """
		for n_sub in self.iterleaf :
			if n_sub.tag == tag and n_sub.ident == ident :
				return n_sub
		raise KeyError("tag={0}, ident={1}".format(tag, ident))
		
	def __repr__(self) :
		return "<{0}.{1}#{2} @{3:08X}>".format(self.space, self.tag, self.ident, id(self))
		
	def pick_tag(self, tag) :
		for n_sub in self.iterleaf :
			if n_sub.tag == tag :
				return n_sub
		raise KeyError("pick_tag({0}, {1})".format(repr(self), tag))
	
	def pick_ident(self, ident) :
		for n_sub in self.iterleaf :
			if n_sub.ident == ident :
				return n_sub
		raise KeyError("ident={0}".format(ident))
		
	def as_line(self) :
		a = Line()
		a.pos = copy.copy(self.pos)
		a.nam = copy.copy(self.nam)
		a.flag = copy.copy(self.flag)
		a.style = copy.copy(self.style)
		return a
		
	def _get_module_class(self) :
		if self.space is None :
			module_name = 'oaktree'
			class_name = 'Leaf'
		else :
			module_name = self._module_prefix + self.space
			class_name = self.tag + self._class_suffix
		return module_name, class_name
			
	def _re_load(self, * pos, ** nam) :
		# post parsing hook should be subclassed if needed
		pass

	def _re_class(self, cls=None) :
		if cls is None and self.space is not None :
			module_name, class_name = self._get_module_class()
			try :
				mod = importlib.import_module(module_name)
				cls = mod.__getattribute__(class_name)
			except ImportError :
				_debug_class_not_found("ImportError", module_name, class_name)
			except AttributeError :
				_debug_class_not_found("AttributeError", module_name, class_name)
		if cls is not None and issubclass(cls, Leaf) :
			self.__class__ = cls
		return self
		
	def _re_space(self) :
		#dbg#print(self.space, self.parent.space if self.parent is not None else '***')
		if self.parent is not None :
			if self.space is None :
				self.space = self.parent.space
			elif self.space.startswith('.') :
				self.space = self.parent.space + self.space
		
	def _re_indent(self) :
		#print("okatree.Leaf._re_indent(", self.tag, self._indent_mode, ")", end=' => ')
		if self._indent_mode is None :
			# if no indentation mode is defined, try to guess the best one
			if len(self.subleaf) == 0 or self.parent is None:
				if self.parent is not None and self.parent._indent_mode is not None :
					self._indent_mode = min(self.parent._indent_mode + 1, oaktree.INLINE)
				else :
					self._indent_mode = oaktree.TREE
			elif ''.join(i.strip() for i in self.subtext) == '' :
				self._indent_mode = oaktree.TREE
				self.sub = self.subleaf
			else :
				self._indent_mode = oaktree.CONTAINER
		
		if self._indent_mode == oaktree.TREE :
			self.sub = self.purged_sub
			
		elif self._indent_mode == oaktree.CONTAINER and len(self.sub) > 0 :
			if isinstance(self.sub[0], str) :
				self.sub[0] = self.sub[0].lstrip()
			if isinstance(self.sub[-1], str) :
				self.sub[-1] = self.sub[-1].rstrip()
		
	def _post_parsing(self) :
		leaf_list = list(self.walk_breadth())
		for n_leaf in leaf_list :
			n_leaf._re_space()
			n_leaf._re_class()
			n_leaf._re_indent()
			n_leaf._re_load()	
	
	@property
	def subleaf(self) :
		""" return all Leaf in sub-items and only Leaf """
		return [c for c in self.sub if isinstance(c, Leaf)]
		
	def __iter__(self) :
		return self.iterleaf

	@property
	def iterleaf(self) :
		""" iter in sub-Leaf only """
		return (i for i in self.sub if isinstance(i, Leaf))
		
	@property
	def subtext(self) :
		return [c for c in self.sub if isinstance(c, str)]
				
	@property
	def purged_sub(self) :
		return [
			i for i in self.sub
			if not isinstance(i, str) or i.strip() != ''
		]
		
	def __copy__(self) :
		n_copy = self.__class__()
		
		n_copy.tag = self.tag
		n_copy.nam = self.nam
		n_copy.pos = self.pos
		n_copy.ident = self.ident
		n_copy.space = self.space
		n_copy.flag = self.flag
		n_copy.style = self.style

		return n_copy
		
	def attach(self, * other_list) :
		""" attach either a Leaf, or an object (text ...) """
		#print('oaktree.Leaf.attach():', type(other))
		for other in other_list :
			if isinstance(other, str) :
				#if other.strip() != '' :
				self.sub.append(other)
			elif isinstance(other, Leaf) :
				other.parent = self
				self.sub.append(other)
			else :
				self.sub.append(other)
		return other_list[0]
		
	def grow(self, tag=None, ident=None, space=None, pos=None, nam=None, flag=None, style=None, indent_mode=None, cls=None) :
		""" make a new Leaf and append it, if you want to subclass use _cls """
		
		if cls is None :
			cls = Leaf
		if space is None :
			space = self.space
		n_leaf = cls(tag, ident, space, pos, nam, flag, style, indent_mode)
		self.attach(n_leaf)
		return n_leaf
		
	def pick_or_grow(self, key, tag=None, ident=None, space=None, pos=None, nam=None, flag=None, style=None, indent_mode=None, cls=None) :
		if key not in self.sub_dict :
			self.sub_dict[key] = self.grow(tag, ident, space, pos, nam, flag, style, indent_mode, cls)
		return self.sub_dict[key]
				
	def walk_depth(self, start=None, stop=None, _depth=0) :
		if _walk_limit(start, stop, _depth) :
			yield self
		for child in self.iterleaf :
			yield from child.walk(start, stop, _depth+1)
			
	walk = walk_depth

	def walk_breadth(self, start=None, stop=None, _depth=0) :
		if _depth == 0 and _walk_limit(start, stop, _depth) :
			yield self
		for n_sub in self.iterleaf :
			if _walk_limit(start, stop, _depth+1) :
				yield n_sub
		for n_sub in self.iterleaf :
			yield from n_sub.walk_breadth(start, stop, _depth+1)
			
	def ancestor(self, n=None) :t
		if n is None :
			stack = [self,]
			n_leaf = self
			while n_leaf.parent is not None :
				stack.append(n_leaf.parent)
				n_leaf = n_leaf.parent
			return reversed(stack)
		else :
			n_leaf = self
			for i in range(n) :
				n_leaf = n_leaf.parent
			return n_leaf
		
	def trim(self) :
		""" remove all sub elements """
		self.sub = list()
		return self

	def add_text(self, txt) :
		""" append a string to the leaf, return self """
		if isinstance(txt, str) :
			if txt.strip() != '' :
				self.sub.append(txt)
		else :
			raise ValueError("append(): first argument must be a string")
		return self

	def get_text(self, sep='') :
		s = list()
		for n_child in self.sub :
			if isinstance(n_child, Leaf) :
				s.append(n_child.get_text(sep))
			else :
				s.append(str(n_child))
		return sep.join(s)
		
	def set_text(self, txt) :
		""" existing children are cleared, the only child is a text """
		self.sub = [str(txt),]
		return self
		
	def chop(self) :
		if self.parent is not None :
			del self.parent.sub[self.parent.sub.index(self)]
			
	def replace(self, n_leaf) :
		""" replace the current self by n_leaf, at the same place in the tree """
		if self.parent is not None :
			# the existing leaf is attached to a tree
			i = self.parent.sub.index(self)
			n_leaf.parent = self.parent
			self.parent.sub[i] = n_leaf
		# return the new leaf
		return n_leaf
				
	def select_tag_Line(self, tag, Line_key, Line_value, max_depth=None) :
		s = Select()
		for n in self.walk() :
			if n.tag == tag :
				try :
					if n[Line_key] == Line_value :
						s.attach(n)
				except (IndexError, KeyError) :
					pass
		return s
				
	def select_nam(self, key, value, max_depth=None) :
		#dbg("<{0}#{1}>.select_nam(key={2}, value={3})".format(self.tag, self.ident, key, value))
		s = Select()
		for node in self.walk(to_depth=max_depth) :
			if key in node.nam and value == node.nam[key] :
				s.sub.append(node)
		return s
		
	def subselect_tag(self, * key_list) :
		s = list()
		for n_sub in self.subleaf :
			if n_sub.tag in key_list :
				s.append(n_sub)
		return s
		
	def select_tag(self, * key, stop=None) :
		n_select = Select()
		for n_leaf in self.walk(stop=stop) :
			if n_leaf.tag in key :
				n_select.sub.append(n_leaf)
		return n_select
		
	def select_style(self, style) :
		n_select = Select()
		for n_leaf in self.walk() :
			if style in n_leaf.style :
				n_select.sub.append(n_leaf)
		return n_select

	def pick_parent(self, tag) :
		""" climb the tree to find the first parent leaf, whose self.tag == tag
		if none can be found, return None
		"""
		while self.tag != tag :
			if self.parent is None :
				return None
			self = self.parent
		return self

	def find_ident(self, ident) :
		""" return the first leaf whose ident match """
		for n in self.walk() :
			if not isinstance(n, Leaf) :
				continue
			if n.ident == ident :
				return n
				
	def find_tag_ident(self, tag, ident) :
		""" return the first leaf whose tag and ident match """
		for n_sub in self.walk() :
			if isinstance(n_sub, Leaf) :
				print("find_tag_ident", n_sub.tag, n_sub.ident)
				if n_sub.ident == ident and n_sub.tag == tag :
					return n_sub
		return None
		
	def find_style(self, name) :
		""" return the first leaf whose flag is present """
		for n_sub in self.walk() :
			if isinstance(n_sub, Leaf) :
				if name in n_sub.style :
					return n_sub
		return None
		
	def find_tag_nam(self, tag, key, value) :
		""" return the first leaf whose tag and nam match """
		for n_sub in self.walk() :
			if isinstance(n_sub, Leaf) :
				if n_sub.tag == tag and key in n_sub.nam and n_sub[key] == value :
					return n_sub
		return None		

	def select_nam(self, key, value, start=None, stop=None) :
		s = Select()
		for n in self.walk(start, stop) :
			if not isinstance(n, Leaf) :
				continue
			if key in n.nam and n.nam[key] == value :
				s.sub.append(n)
		return s
		
	def select_tag_nam(self, tag, key, value, start=None, stop=None) :
		n_select = Select()
		for n in self.walk(start, stop) :
			if n.tag == tag and key in n.nam and n.nam[key] == value :
				n_select.sub.append(n)
		return n_select
		
	@property
	def first(self) :
		for n_sub in self.sub :
			if isinstance(n_sub, Leaf) :
				return n_sub
		
	@property
	def last(self) :
		for n_sub in reversed(self.sub) :
			if isinstance(n_sub, Leaf) :
				return n_sub

class Select(Leaf) :
	tag = '__select__'
	""" this node is specialised in node selection """
	
	def __iter__(self) :
		return (i for i in self.sub if isinstance(i, Leaf))
		
	def __bool__(self) :
		return True if self.subleaf else False

