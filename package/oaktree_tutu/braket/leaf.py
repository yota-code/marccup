#!/usr/bin/env python3

import io

import oaktree

from oaktree.braket.common import *

from oaktree.auto_rw import auto_write

from oaktree.braket.line import Line

_esc_leaf = [('&', '&esc;'), ('|', '&pipe;'), ('>', '&cbkt;'), ('<', '&obkt;')]

class Leaf(oaktree.Leaf, Line) :
	
	@auto_write
	def compose(self, _depth=0, _aw=None) :
		
		if self._indent_mode is None :
			self._re_indent()
		
		before_header, after_header, before_footer, after_footer = indentation(self._indent_mode, _depth)
		
		_aw(before_header)
		_aw(markup_begin)
		Leaf._compose_header(self, _aw=_aw)
		if self.sub :
			_aw(markup_separator)
			_aw(after_header)
			previous_was_str = False
			for k in self.sub :
				if isinstance(k, oaktree.Leaf) :
					if previous_was_str :
						_aw('\n')
					Leaf.compose(k, _depth+1, _aw=_aw)
					previous_was_str = False
				else :
					if previous_was_str :
						_aw(markup_separator)
						if self._indent_mode < oaktree.CONTAINER :
							_aw('\n')
					_aw(protect(k, _esc_leaf))
					previous_was_str = True
			if previous_was_str and self._indent_mode < oaktree.CONTAINER :
				_aw('\n')
			_aw(before_footer)
			_aw(markup_separator)
			Leaf._compose_footer(self, _aw=_aw)
		_aw(markup_end)
		_aw(after_footer)
		
	@auto_write
	def _compose_space(self, _aw=None) :
		if self.parent is None :
			if self.space is None :
				return
			else :
				space = self.space
		else :
			if self.space is None :
				return
			else :
				if self.parent.space is None :
					space = self.space
				else :
					if self.parent.space == self.space :
						return
					else :
						if self.space.startswith(self.parent.space + '.') :
							space = self.space[len(self.parent.space):]
						else :
							space = self.space
		_aw("{0}{1}".format(space, space_separator))
		
	@auto_write
	def _compose_ident(self, _aw=None) :
		if self.ident is not None :
			_aw("{0}{1}".format(ident_separator, self.ident))
		
	@auto_write
	def _compose_header(self, _aw=None) :
		Leaf._compose_space(self, _aw=_aw)
		_aw(self.tag)
		Leaf._compose_ident(self, _aw=_aw)
		Line.compose(self, _aw=_aw)
		
	@auto_write
	def _compose_footer(self, _aw=None) :
		if self.parent is None :
			Leaf._compose_space(self, _aw=_aw)
			_aw(self.tag)
		
	def _parse_header(self, s) :
		head, null, line = s.partition(' ')
		try :
			res = space_tag_ident_rec.search(head).groupdict()
		except AttributeError :
			print(s)
			raise
		
		if res['space'] is not None :
			self.space = res['space']
		self.tag = res['tag']
		if res['ident'] is not None :
			self.ident = res['ident']
		
		Line.parse(self, line)
				
	def parse(self, s, n=0, depth=0) :
		#print(">>>\t{0}{1:08X} {2!r}".format('>>>\t'*depth, id(self), s[n:n+32]))
		status = 0
		brace = 0
		prev_n = n
		while n < len(s) :
			c = s[n]
			n += 1
			if c == '{' :
				brace += 1
			elif c == '}' :
				brace -= 1
			if status == 0 : # before the header
				if c == '<' : # begining of the header
					status = 1
					prev_n = n
					brace = 0
			elif status == 1 : # inside the header
				if brace == 0 and c == '|' : # end of the header
					self._parse_header(s[prev_n:n-1])
					prev_n = n
					status = 2
				elif c == '>' :
					if brace != 0 :
						raise SyntaxError("non matching braket before: ...{0}".format(s[n-15:n]))
					self._parse_header(s[prev_n:n-1])
					break
			elif status == 2 :
				if c == '<' :
					self.add_text(restore(s[prev_n:n-1], _esc_leaf).strip())
					n_sub, n = Leaf().parse(s, n-1, depth+1)
					self.attach(n_sub)
					prev_n = n
				elif c == '|' and brace == 0 :
					self.add_text(restore(s[prev_n:n-1], _esc_leaf).strip())
					prev_n = n
				elif c == '>' :
					if brace != 0 :
						raise SyntaxError("non matching braces before: ...{0}".format(s[n-15:n]))
					prev_n = n
					break
		if status <= 0 :
			return None, n
		if depth == 0 :
			self._post_parsing()
		return self, n

