#!/usr/bin/env python3

import oaktree

tag_begin = r'<'
tag_end = r'>'
tag_slash = r'/'

space_separator = r':'

line_begin = r'="'
line_end = r'"'

def indentation(indent_mode, depth) :
	if indent_mode == oaktree.INLINE :
		return '', '', '', ''
	elif indent_mode == oaktree.CONTAINER :
		return '\t' * depth, '', '', '\n'
	else :
		return '\t' * depth, '\n', '\t' * depth, '\n'
		
