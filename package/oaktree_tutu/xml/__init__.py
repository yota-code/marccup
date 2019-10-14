#!/usr/bin/env python3

import sys
import re

import oaktree

from oaktree.xml.common import *

from oaktree.xml.line import Line
from oaktree.xml.leaf import Leaf

def dump(n_leaf, output=None, stylesheet=None, max_depth=None) :
	if not isinstance(n_leaf, oaktree.Leaf) :
		raise ValueError("{0} is not an oaktree.Leaf instance".format(n_leaf.__class__))
	
	if isinstance(output, str) :
		# output is a string, take it as a file name, try to write to it
		with open(output, 'wt', encoding='utf8') as fid :
			fid.write('<?xml version="1.0" encoding="utf-8"?>\n')
			if stylesheet is not None :
				fid.write('<?xml-stylesheet type="text/css" href="{0}" ?>\n'.format(stylesheet))
			Leaf.compose_file(n_leaf, fid, max_depth)
		
	elif output is None :
		# output is None, return a string
		return Leaf.compose_string(n_leaf, max_depth)
		
	else :
		# else try to use the output.write method
		Leaf.compose_file(n_leaf, output, max_depth)
		
def pprint(n_leaf, max_depth=None) :
	dump(n_leaf, sys.stdout, max_depth)
	
def load_file(path) :
	with open(path, 'rt', encoding='utf8') as fid :
		return load_string(fid.read())
			
def load_string(s) :
	s = remove_useless(s)
	n_leaf, null = Leaf().parse_string(s)
	return n_leaf
	
def load_string_iter(s) :
	curs = 0
	while True :
		n_leaf, curs = Leaf().parse_string(s, curs)
		if n_leaf is None :
			break
		else :
			yield n_leaf
			
			
