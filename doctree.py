#!/usr/bin/env python3

import re

def _walk_limit(start=None, stop=None, _depth=0) :
	return (
		(start is None or _depth >= start) and 
		(stop is None or _depth < stop) 
	)

class TxtReq() :
	def __init__(self, txt, req=None) :
		self.txt = txt
		self.req = req

class Leaf() :

	def __init__(self, tag=None, ident=None, space=None, pos=None, nam=None, flag=None, style=None) :

		self.tag = tag
		self.ident = ident
		self.space = space

		self.pos = list(pos) if pos is not None else list()
		self.nam = dict(nam) if nam is not None else dict()
		self.flag = set(flag) if flag is not None else set()
		self.style = set(style) if style is not None else set()

		self.parent = None
		self.sub = list()

	def __str__(self) :
		return '\n'.join(self._to_str())

	def __repr__(self) :
		return f"<{self._to_str_space_tag_ident()} @{id(self):08X}>"

	def _to_str(self, stack=None, depth=0) :
		if stack is None :
			stack = list()

		line = ('\t' * depth) + '<' + ' '.join(
			[self._to_str_space_tag_ident(),] +
			sorted(self.pos) + [
				'{k}={self.nam[k]}' for k in sorted(self.nam)
			] + sorted(self.flag) + [
				'@{i}' for i in sorted(self.style)
			]
		) + '|'

		if len(self.sub) == 1 and isinstance(self.sub[0], str) :
			line += self.sub[0] + '|>'
			stack.append(line)
		else :
			stack.append(line)
			for obj in self.sub :
				if hasattr(obj, "_to_str") :
					obj._to_str(stack, depth+1)
				else :
					stack.append(('\t'*(depth+1)) + str(obj))
			stack.append(('\t'*depth) + '|>')
	
		return stack

	def _to_str_space_tag_ident(self) :
		return (
			((self.space + '.') if self.space is not None else '') + 
			self.tag + 
			(('#' + self.ident) if self.ident is not None else '')
		)

	@property
	def root(self) :
		root = self
		while root.parent is not None :
			root = root.parent
		return root

	@property
	def is_root(self) :
		return self.parent is None

	#def __repr__(self) :
	#	return "<{0}.{1}#{2} @{3:08X}>".format(self.space, self.tag, self.ident, id(self))

	@property
	def subleaf(self) :
		""" return all Leaf in sub-items and only Leaf """
		return [c for c in self.sub if isinstance(c, Leaf)]

	@property
	def subtext(self) :
		return [c for c in self.sub if isinstance(c, str)]

	def __iter__(self) :
		return self.iterleaf

	@property
	def iterleaf(self) :
		""" iter in sub-Leaf only """
		return (i for i in self.sub if isinstance(i, Leaf))

	def grow(self, tag=None, ident=None, space=None, pos=None, nam=None, flag=None, style=None, cls=None) :
		""" make a new Leaf and append it, if you want to subclass use _cls """
		
		if cls is None :
			cls = Leaf
		if space is None :
			space = self.space

		leaf = cls(tag, ident, space, pos, nam, flag, style)
		self.attach(leaf)
		return leaf

	def attach(self, * other_list) :
		""" attach either a Leaf, or an object (text ...) """
		for other in other_list :
			if isinstance(other, str) :
				self.sub.append(other)
			elif isinstance(other, Leaf) :
				other.parent = self
				self.sub.append(other)
			else :
				self.sub.append(other)
		return other_list[0]

	def walk_depth(self, start=None, stop=None, _depth=0) :
		if _walk_limit(start, stop, _depth) :
			yield self
		for child in self.iterleaf :
			yield from child.walk(start, stop, _depth+1)

	def walk_breadth(self, start=None, stop=None, _depth=0) :
		if _depth == 0 and _walk_limit(start, stop, _depth) :
			yield self
		for n_sub in self.iterleaf :
			if _walk_limit(start, stop, _depth+1) :
				yield n_sub
		for n_sub in self.iterleaf :
			yield from n_sub.walk_breadth(start, stop, _depth+1)

	def ancestor(self, n=None) :
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

	def add_alinea(self, txt) :
		rec = re.compile(r'^\s*(?P<line>.*?)\s*(§(?P<ident>[0-9]+))?$')
		res = rec.match(txt)
		ident = int(res.group('ident')) if res.group('ident') is not None else None
		self.grow('alinea', ident=str(ident)).add_text(res.group('line'))

