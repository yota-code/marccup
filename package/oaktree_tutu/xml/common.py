#!/usr/bin/env python3

import re

import oaktree

tag_begin = r'<'
tag_end = r'>'
tag_slash = r'/'

space_separator = r':'

line_begin = r'="'
line_end = r'"'

attribute_rec = re.compile(r'\b((?P<space>\w+):)?(?P<key>\w+)="(?P<value>.*?)"', re.DOTALL | re.MULTILINE | re.UNICODE)

def indentation(indent_mode, depth) :
	if indent_mode == oaktree.INLINE :
		return '', '', '', ''
	elif indent_mode == oaktree.CONTAINER :
		return '\t' * depth, '', '', '\n'
	else :
		return '\t' * depth, '\n', '\t' * depth, '\n'

xml_comment_rec = re.compile(r'<!--.*?-->', re.DOTALL | re.MULTILINE)
xml_declaration_rec = re.compile(r'<\?.*?\?>', re.DOTALL | re.MULTILINE)
def remove_useless(s) :
	s = xml_comment_rec.sub('', s)
	s = xml_declaration_rec.sub('', s)
	return s
	
	
