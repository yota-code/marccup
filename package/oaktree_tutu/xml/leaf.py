#!/usr/bin/env python3

import io

import oaktree

from oaktree.xml.common import *

from oaktree.xml.line import Line 

STATE_OUT = 0
STATE_HEADER = 1
STATE_IN = 2
STATE_FOOTER = 3

dbg = (lambda * n_arg, ** p_arg : None)

class Leaf(oaktree.Leaf, Line) :
	
	def compose_string(self, max_depth=None, _depth=0) :
		fid = io.StringIO()
		Leaf.compose_file(self, fid, max_depth, _depth)
		return fid.getvalue()
		
	__str__ = compose_string
	
	def compose_file(self, fid, max_depth=None, _depth=0) :
		w = fid.write
		
		if self._indent_mode is None :
			self._re_indent()
		
		before_header, after_header, before_footer, after_footer = indentation(self._indent_mode, _depth)
	
		w(before_header)
		w(tag_begin)
		w(Leaf._compose_header(self))
		if self.sub :
			w(tag_end)
			w(after_header)
			if max_depth != None and _depth >= max_depth :
				w(' ... ')
			else :
				previous_was_str = False
				for k in self.sub :
					if isinstance(k, oaktree.Leaf) :
						Leaf.compose_file(k, fid, max_depth, _depth+1)
						previous_was_str = False
					else :
						w(str(k))
						previous_was_str = True
			w(before_footer)
			w(tag_begin+tag_slash)
			w(Leaf._compose_footer(self))
		else :
			w(' '+tag_slash)
		w(tag_end)
		w(after_footer)
		
	def _compose_header(self) :
		space = '' if (self.space is None or self.space == self.root.space) else self.space + space_separator
		tag = self.tag
		ident = '' if self.ident is None else ' id="{0}"'.format(self.ident)
		line = Line.compose_string(self)
		return 	space + tag + ident + (' ' if line else '') + line
		
	def _compose_footer(self) :
		return self.tag
		
	def _parse_header(self, txt) :
		#print("{0:x}.parse_header({1}...)".format(id(self), txt[:12]))
		head, null, line = txt.partition(' ')
		self.tag = head
				
		Line.parse_string(self, line)
		
	def parse_string(self, txt, curs=0, depth=0) :
		dbg("{0} parse_string({1}...)".format(' ==>'*depth, repr(txt[curs:curs+12])))
		state = 0
		prev = curs
		while curs < len(txt) :
			c = txt[curs]
			curs += 1
			dbg(repr(c), '::', depth, '::', repr(txt[curs:curs+12]))
			if state == STATE_OUT :
				if c == tag_begin :
					state = STATE_HEADER
					dbg("{0} OUT -> HEADER : {1} {2} {3}".format('  ->'*depth, repr(txt[curs-12:curs-1]), repr(txt[curs-1]), repr(txt[curs:curs+12])))
					prev = curs
			elif state == STATE_HEADER :
				if c == tag_end :
					state = STATE_IN
					dbg("{0} HEADER -> IN : {1} {2} {3}".format('  ->'*depth, repr(txt[curs-12:curs-1]), repr(txt[curs-1]), repr(txt[curs:curs+12])))
					if txt[curs-2] == tag_slash :
						# self closing element
						state = STATE_FOOTER
						dbg("{0} HEADER -> FOOTER : {1} {2} {3}".format('  ->'*depth, repr(txt[curs-12:curs-1]), repr(txt[curs-1]), repr(txt[curs:curs+12])))
						self._parse_header(txt[prev:curs-2])
						break
					else :
						self._parse_header(txt[prev:curs-1])
					prev = curs	
			elif state == STATE_IN :
				if c == tag_begin :
					if txt[curs] == tag_slash :
						# closing tag
						self.text(txt[prev:curs-1])
						state = STATE_FOOTER
						dbg("{0} IN -> FOOTER : {1} {2} {3}".format('  ->'*depth, repr(txt[curs-12:curs-1]), repr(txt[curs-1]), repr(txt[curs:curs+12])))
					else :
						n_sub, curs = Leaf().parse_string(txt, curs-1, depth+1)
						self.attach(n_sub)
						prev = curs
			elif state == STATE_FOOTER :
				if c == tag_end :
					break
		dbg("{0} parse_string({1}...)".format('<== '*depth, repr(txt[curs:curs+12])))
		return self, curs

