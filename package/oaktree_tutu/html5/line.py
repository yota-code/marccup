#!/usr/bin/env python3

import oaktree

from oaktree.braket.common import *

def escape(s) :
	s = str(s)
	s = s.replace('&', '&amp;')
	s = s.replace('"', '&quot;')
	return s

class Line(oaktree.Line) :
	
	def compose_string(self) :
		s = list()
		s += ['_pos_{0}="{1}"'.format(*i) for i in enumerate(self.pos)]
		s += ['{0}="{1}"'.format(i, escape(self.nam[i])) for i in sorted(self.nam)]
		if len(self.style) > 0 :
			s += ['class="{0}"'.format(' '.join(sorted(self.style))),]
		s += ['{0}'.format(i) for i in sorted(self.flag)]
		return ' '.join(s)
		
	__str__ = compose_string
	
	def compose_file(self, fid) :
		fid.write(self.compose_string())
		
	def parse_string(self, s) :
		s = consume(s, line_nam_rec, self._rep_nam)
		s = consume(s, line_pos_rec, self._rep_pos)
		s = consume(s, line_style_rec, self._rep_style)
		s = consume(s, line_flag_rec, self._rep_flag)
		return self
		
	def _rep_nam(self, res) :
		self.nam[res.group('name')] = res.group('value')
		
	def _rep_pos(self, res) :
		self.pos.append(res.group('value'))
		
	def _rep_style(self, res) :
		self.style.add(res.group('name'))
		
	def _rep_flag(self, res) :
		self.flag.add(res.group('name'))


