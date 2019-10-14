#!/usr/bin/env python3

import re, io

from oaktree import Node, Text

tag_begin = r'<'
tag_end = r'>'
tag_slash = r'/'

space_separator = r':'

attribute_begin = r'="'
attribute_end = r'"'

#rec_named = re.compile(r'([a-z_]+){0}(.*?){1}'.format(
#	re.escape(attribute_begin), re.escape(attribute_end)
#))
#
#rec_positional = re.compile(r'\s{0}(.*?){1}'.format(
#	re.escape(attribute_begin), re.escape(attribute_end)
#))
#
#rec_style = re.compile(r'\s{0}([a-z_]+)(?=([\s|>]|$))'.format(
#	re.escape(attribute_style)
#))
#
#rec_flag = re.compile(r'\s(!?[a-z_]+)(?=([\s|>]|$))')
#
#rec_space_tag_ident = re.compile(r'^((?P<space>[a-z_]+){0})?(?P<tag>[a-z_]+)({1}(?P<ident>[a-z0-9A-F\-]+))?'.format(
#		re.escape(space_separator), re.escape(ident_separator),
#))


			
def dump_node(self, file, depth=0, max_depth=None) :
	_node_type = 0
	if self._node_type == 0 :
		before_header = '\t' * depth
		after_header = '\n'
		before_footer = '\t' * depth
		after_footer = '\n'
	elif self._node_type == 1 :
		before_header = '\t' * depth
		after_header = ''
		before_footer = ''
		after_footer = '\n'
	else :
		before_header = ''
		after_header = ''
		before_footer = ''
		after_footer = ''
		

	w = file.write
	w(before_header)
	w(tag_begin)
	w(_compose_header(self))
	if self.children :
		w(tag_end)
		w(after_header)
		if max_depth != None and depth >= max_depth :
			w(' ... ')
		else :
			for k in self.children :
				if isinstance(k, Node) :
					dump_node(k, file, depth+1, max_depth)
				else :
					w(str(k))
		w(before_footer)
		w(tag_begin + '/')
		w(_compose_footer(self))
	else :
		w(' /')
	w(tag_end)
	w(after_footer)
			
def _compose_header(self) :
	space = ''
	#space = self._space + space_separator if self._space != self.parent._space else ''
	
	if self.ident != None :
		self.nam['id'] = self.ident
		
	if len(self.style) > 0 :
		self.nam['class'] = ' '.join(self.style)
		
	for n, i in enumerate(self.pos) :
		self.nam['_pos_{0}'.format(n)] = str(i)
		
	for i in self.flag :
		if i[0] == '!' :
			b = False
			s = i[1:]
		else :
			b = True
			s = i
		self.nam['_flag_' + s] = str(b)
	
	h = [space + self.tag,]
	h += [str(i) + attribute_begin + str(self.nam[i]) + attribute_end for i in self.nam]
	h += [i for i in self.flag]
	
	return ' '.join(h)
	
def _compose_footer(self) :
	return self.tag

def _parse_header(self, s) :
	
	res = rec_space_tag_ident.search(s).groupdict()
	
	self._space = res['space'] if res['space'] != "__none__" else None
	self.tag = res['tag']
	self.ident = res['ident']
			
	self.re_class()
	
	for i in rec_named.finditer(s) :
		self.nam[i.group(1)] = i.group(2)
		
	for i in rec_positional.finditer(s) :
		self.pos.append(i.group(1))
		
	for i in rec_style.finditer(s) :
		self.style.add(i.group(1))
		
	for i in rec_flag.finditer(s) :
		self.flag.add(i.group(1))
			
def load(line) :
	line = line.strip()
	tree = Node('__tmp__')
	load_node(tree, line)
	return tree.children[0]
	
def dump(a, file=None) :
	if file == None :
		file = io.StringIO()
	dump_node(a, file)
	
