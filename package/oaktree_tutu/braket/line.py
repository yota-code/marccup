#!/usr/bin/env python3

import io

import oaktree

from oaktree.braket.common import *

from oaktree.braket.auto_rw import auto_write


_esc_line_value = [('&', '&esc;'), ('|', '&pipe;'), ('>', '&cket;'), ('<', '&oket;'), ('}', '&cbra;'), ('{', '&obra;')]

_begin = r'{'
_end = r'}'
_style = r'@'

re_flag = re.UNICODE | re.MULTILINE | re.DOTALL

_nam_rec = re.compile(r'(?P<name>\w+){0}(?P<value>.*?){1}'.format(re.escape(_begin), re.escape(_end)), re_flag)
_pos_rec = re.compile(r'{0}(?P<value>.*?){1}'.format(re.escape(_begin), re.escape(_end)), re_flag)
_style_rec = re.compile(r'{0}(?P<name>\w+)'.format(re.escape(_style)), re_flag)
_flag_rec = re.compile(r'(?P<name>!?\w+)', re_flag)

class Line(oaktree.Line) :
				
	@auto_write
	def compose(self, _aw=None) :
		""" compose to a StringIO-like object """
		s = ' '.join(
			["{{{0}}}".format(protect(i, _esc_line_value)) for i in self.pos]
			+ ["{0}{{{1}}}".format(i, protect(self.nam[i], _esc_line_value)) for i in sorted(self.nam)]
			+ ["{0}".format(i) for i in sorted(self.flag)]
			+ ["@{0}".format(i) for i in sorted(self.style)]
		)
		if s.strip() != '' :
			_aw(' ')
			_aw(s)
		
	def __str__(self) :
		return self.compose()
		
	def __repr__(self) :
		return str(self.__dict__)
		
	def parse(self, s) :
		s_init = s
		s = consume(s, _nam_rec, self._rep_nam)
		s = consume(s, _pos_rec, self._rep_pos)
		s = consume(s, _style_rec, self._rep_style)
		s = consume(s, _flag_rec, self._rep_flag)
		if s.strip() :
			raise Warning("Line:remaining elements not parsed:{0} in {1}".format(s, s_init))
		return self
		
	def _rep_nam(self, res) :
		self.nam[res.group('name')] = restore(res.group('value'), _esc_line_value)
		
	def _rep_pos(self, res) :
		self.pos.append(restore(res.group('value'), _esc_line_value))
		
	def _rep_style(self, res) :
		self.style.add(res.group('name'))
	
	def _rep_flag(self, res) :
		self.flag.add(res.group('name'))

if __name__ == '__main__' :
	s = 'tutu field{inside, value & demo} !machin @smoking {other various &cket; stuff} {1.33} list{[1,2,3,]} map{&obra;1:4,2:"5 4"&cbra;}'
	print(s)
	a = str(Line().parse(s))
	print(repr(Line().parse(s)))
	b = str(Line().parse(a))
	print(b)
	if a != b :
		raise ValueError
			
