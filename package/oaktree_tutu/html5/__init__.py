#!/usr/bin/env python3

import sys
import re

from pathlib import Path

import oaktree

from oaktree.html5.common import *
from oaktree.auto_rw import auto_read

from oaktree.html5.line import Line
from oaktree.html5.leaf import Leaf

def dump(n_leaf, output=None) :
	return Leaf.compose(n_leaf, _aw=output)
	
#	if not isinstance(n_leaf, oaktree.Leaf) :
#		raise ValueError("{0} is not an oaktree.Leaf instance".format(n_leaf.__class__))
#	
#	if isinstance(output, str) :
#		# output is a string, take it as a file name, try to write to it
#		with open(output, 'wt', encoding='utf8') as fid :
#			Leaf.compose_file(n_leaf, fid, max_depth)
#		
#	elif output is None :
#		# output is None, return a string
#		return Leaf.compose_string(n_leaf, max_depth)
#		
#	else :
#		# else try to use the output.write method
#		Leaf.compose_file(n_leaf, output, max_depth)
		
def print(n_leaf, output=sys.stdout) :
	Leaf.compose(n_leaf, _aw=output)
	
def load(in_arg) :
	if isinstance(in_arg, str) :
		try :
			with open(in_arg, 'rt', encoding='utf8') as fid :
				txt = fid.read()
				n_leaf, null = Leaf().parse_string(txt)
				return n_leaf
		except :
			raise
			
def boilerplate(title, css=None, embedded_css=False) :
	h_html = oaktree.html5.Leaf('html')
	h_head = h_html.grow('head')
	h_head.grow('title').set_text(title)
	h_head.grow('meta', nam={'charset':"utf-8"})
	if embedded_css :
		h_head.grow('style', indent_mode=oaktree.TREE).set_text(auto_read(css))
	else :
		h_head.grow('link', nam={'href':str(css), 'rel':"stylesheet", 'type':"text/css"})
	h_body = h_html.grow('body')
	return h_html, h_head, h_body

