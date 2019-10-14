#!/usr/bin/env python3

import re

attribute_begin = r'{'
attribute_end = r'}'
attribute_style = r'@'

attribute_nam_rec = re.compile(r'(?P<name>\w+){0}(?P<value>.*?){1}'.format(
	re.escape(attribute_begin), re.escape(attribute_end)
))
attribute_pos_rec = re.compile(r'{0}(?P<value>.*?){1}'.format(
	re.escape(attribute_begin), re.escape(attribute_end)
))
attribute_style_rec = re.compile(r'{0}(?P<name>\w+)'.format(re.escape(attribute_style)), re.UNICODE)
attribute_flag_rec = re.compile(r'(?P<name>!?\w+)')

class Attribute() :
	def __init__(self, * pos_arg, ** nam_arg) :
		
		self.pos = list(pos_arg)
		self.nam = dict(nam_arg)
		self.style = set()
		self.flag = set()

	def compose_attribute(self) :
		stack = list()
		stack += ["{{{0}}}".format(i) for i in self.pos]
		stack += ["{0}{{{1}}}".format(i, self.nam[i]) for i in self.nam]
		stack += ["@{0}".format(i) for i in self.style]
		stack += ["{0}".format(i) for i in self.flag]
		return ' '.join(stack)
		
	__str__ = compose
	
	def __repr__(self) :
		return "Attribute(pos={0}, nam={1}, style={2}, flag={3})".format(self.pos, self.nam, self.style, self.flag)

	def parse_attribute(self, line) :
		line = re_consume(line, attribute_nam_rec, self._parse_attribute_nam)
		line = re_consume(line, attribute_pos_rec, self._parse_attribute_pos)
		line = re_consume(line, attribute_style_rec, self._parse_attribute_style)
		line = re_consume(line, attribute_flag_rec, self._parse_attribute_flag)
		return self
		
	def _parse_attribute_nam(self, res) :
		self.nam[res.group('name')] = res.group('value')
		
	def _parse_attribute_pos(self, res) :
		self.pos.append(res.group('value'))
		
	def _parse_attribute_style(self, res) :
		self.style.add(res.group('name'))
		
	def _parse_attribute_flag(self, res) :
		self.flag.add(res.group('name'))
	
def re_consume(line, rec, func) :
	s = list()
	start = None
	for res in rec.finditer(line) :
		end, next = res.span()
		s.append(line[start:end])
		start = next
		func(res)
	s.append(line[start:])
	return ''.join(s)
	
if __name__ == '__main__' :
	u = 'tutu field{inside value demo} !machin @smoking {other various stuff}'
	a = Attribute().parse(u)
	print(repr(a))
