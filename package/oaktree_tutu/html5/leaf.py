#!/usr/bin/env python3

import io
import html

import oaktree

from oaktree.html5.common import *
from oaktree.html5.line import Line

from oaktree.auto_rw import auto_write

void_element_list = ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr']

class Leaf(oaktree.Leaf, Line) :
	
	def compose_string(self, max_depth=None, _depth=0) :
		fid = io.StringIO()
		Leaf.compose_file(self, fid, max_depth, _depth)
		return fid.getvalue()
		
	__str__ = compose_string
	
	@auto_write
	def compose(self, _depth=0, _aw=None) :
		if _depth == 0 :
			_aw("<!DOCTYPE html>\n")
		
		if self._indent_mode is None :
			self._re_indent()
		
		before_header, after_header, before_footer, after_footer = indentation(self._indent_mode, _depth)
	
		_aw(before_header)
		_aw(tag_begin)
		_aw(Leaf._compose_header(self))
		if self.sub :
			_aw(tag_end)
			_aw(after_header)
			previous_was_str = False
			for n_sub in self.sub :
				if isinstance(n_sub, oaktree.Leaf) :
					Leaf.compose(n_sub, _depth+1, _aw=_aw)
					previous_was_str = False
				else :
					_aw(html.escape(str(n_sub), False))
					previous_was_str = True
			_aw(before_footer)
			_aw(tag_begin+tag_slash)
			_aw(Leaf._compose_footer(self))
		elif self.tag not in void_element_list :
			_aw(tag_end)
			_aw(before_footer)
			_aw(tag_begin+tag_slash)
			_aw(Leaf._compose_footer(self))
		_aw(tag_end)
		_aw(after_footer)
		
	@auto_write
	def _compose_header(self, _aw=None) :
		space = '' if (self.space is None or self.space == self.root.space) else self.space + space_separator
		tag = self.tag
		ident = '' if self.ident is None else ' id="{0}"'.format(self.ident)
		line = Line.compose_string(self)
		_aw(space + tag + ident + (' ' if line else '') + line)
		
	def _compose_footer(self) :
		return self.tag
		
	def _parse_header(self, txt) :
		#print("{0:x}.parse_header({1}...)".format(id(self), txt[:12]))
		head, null, line = txt.partition(' ')
		try :
			res = space_tag_ident_rec.search(head).groupdict()
		except AttributeError :
			print(txt)
			raise
	
		if res['space'] is not None :
			self.space = res['space']
		self._tag = res['tag']
		self.ident = res['ident']
				
		Line.parse_string(self, line)
		
	def parse_string(self, text, n=0, depth=0) :
		#print("{0:x}.parse_string({1}...)".format(id(self), text[n:n+12]))
		status = 0
		brace = 0
		prev_n = n
		while n < len(text) :
			#print(n, text[n:n+16])
			c = text[n]
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
					self._parse_header(text[prev_n:n-1])
					prev_n = n
					brace = 0
					status = 2
				elif c == '>' :
					if brace != 0 :
						raise SyntaxError("non matching braces before: ...{0}".format(text[n-15:n]))
					self._parse_header(text[prev_n:n-1])
					break
			elif status == 2 :
				if c == '<' :
					#print("attach before < :",prev_n, n-1, repr(text[prev_n:n-1]), repr(text[prev_n-10:n-1+10]))
					self.attach(text[prev_n:n-1])
					n_sub, n = Leaf().parse_string(text, n-1, depth+1)
					self.attach(n_sub)
					prev_n = n
				elif c == '|' and brace == 0 :
					#print("attach before < :",prev_n, n-1, repr(text[prev_n:n-1]), repr(text[prev_n-10:n-1+10]))
					self.attach(text[prev_n:n-1])
					prev_n = n
				elif c == '>' :
					if brace != 0 :
						raise SyntaxError("non matching braces before: ...{0}".format(text[n-15:n]))
					prev_n = n
					break
		if status <= 0 :
			return None, n
		if depth == 0 :
			self._post_parsing()
		return self, n

