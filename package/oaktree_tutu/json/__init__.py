#!/usr/bin/env python3


import sys
import re

import oaktree

from oaktree.json.line import Line
from oaktree.json.leaf import Leaf
	
def dump(n_leaf, _output=None, ** n_arg) :
	return Leaf.compose(n_leaf, _aw=_output, ** n_arg)
		
def load(in_arg) :
	if isinstance(in_arg, str) :
		try :
			with open(in_arg, 'rt', encoding='utf8') as fid :
				txt = fid.read()
				n_leaf, null = Leaf().parse_string(txt)
				return n_leaf
		except :
			raise
			
def load_file(s) :
	with open(s, 'rt', encoding='utf8') as fid :
		txt = fid.read()
		n_leaf, null = Leaf().parse_string(txt)
		return n_leaf
			
def load_string(s) :
	n_leaf, null = Leaf().parse_string(s)
	return n_leaf

