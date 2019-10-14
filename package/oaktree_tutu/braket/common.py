#!/usr/bin/env python3

import re, io
import ast

import oaktree

markup_begin = r'<'
markup_end = r'>'
markup_separator = r'|'

space_separator = r':'
ident_separator = r'#'

space_tag_ident_rec = re.compile(
	r'^((?P<space>((\.)?[a-z_]+)+){0})?(?P<tag>[a-z_]+)({1}(?P<ident>\S+))?'.format(
		re.escape(space_separator), re.escape(ident_separator),
))

def try_eval(s) :
	try :
		return ast.literal_eval(s)
	except :
		return s
		
def protect(s, escape_lst) :
	s = str(s)
	for a, b in escape_lst :
		s = s.replace(a, b)
	return s
	
def restore(s, escape_lst) :
	for b, a in reversed(escape_lst) :
		s = s.replace(a, b)
	return s

def consume(line, rec, func) :
	s = list()
	start = None
	for res in rec.finditer(line) :
		end, next = res.span()
		s.append(line[start:end])
		start = next
		func(res)
	s.append(line[start:])
	return ''.join(s)

def indentation(indent_mode, depth) :
	if indent_mode == oaktree.INLINE :
		return '', '', '', ''
	elif indent_mode == oaktree.CONTAINER :
		return '\t' * depth, '', '', '\n'
	else :
		return '\t' * depth, '\n', '\t' * depth, '\n'

	
	
