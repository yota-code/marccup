#!/usr/bin/env python3

import oaktree

from oaktree.xml.common import *

def restore(s) :
	return s.replace('&quot;', '"').replace('&lt;', '<').replace('&amp;', '&')

def protect(s) :
	return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')

class Line(oaktree.Line) :
	
	def compose_string(self) :
		s = list()
		s += ['_pos_{0}="{1}"'.format(*i) for i in enumerate(self.pos)]
		s += ['{0}="{1}"'.format(i, self.nam[i]) for i in sorted(self.nam)]
		if len(self.style) > 0 :
			s += ['class="{0}"'.format(' '.join(sorted(self.style))),]
		return ' '.join(s)
		
	__str__ = compose_string
	
	def compose_file(self, fid) :
		fid.write(self.compose_string())
		
	def parse_string(self, s) :
		for attribute_res in attribute_rec.finditer(s) :
			key = attribute_res.group('key')
			value = restore(attribute_res.group('value'))
			if key == 'id' :
				self.ident = value
			elif key == 'class' :
				self.style |= set(value.split())
			else :
				self.nam[key] = value
		return self
		
	def _rep_nam(self, res) :
		self.nam[res.group('name')] = res.group('value')
		
	def _rep_pos(self, res) :
		self.pos.append(res.group('value'))
		
	def _rep_style(self, res) :
		self.style.add(res.group('name'))
		
	def _rep_flag(self, res) :
		self.flag.add(res.group('name'))


