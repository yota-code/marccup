#!/usr/bin/env python3

"""
braket is the native, and such recommanded, textual representation of the oaktree hierarchy
"""

import sys, os
import re, io
import pathlib

import oaktree

from .leaf import Leaf
from .line import Line

def dump(n_leaf, _output=None) :
	return Leaf.compose(n_leaf, _aw=_output)
	
def load(_input, n_parent=None) :
	"""
	_input: can be a pathlib.Path(), a str() or anything else with a .read() method
	n_parent: is an optionnal parent Leaf() on which, parsed elements are attached
	"""
	if isinstance(_input, pathlib.Path) :
		with _input.open('rt', encoding='utf8') as fid :
			s = fid.read()
	elif isinstance(_input, str) :
		s = _input
	else :
		s = _input.read()
		
	if n_parent is None :
		n_leaf, n = Leaf().parse(s)
		return n_leaf
	else :
		n_tmp, n = cls().parse('<__tmp__|' + s + '|>')
		for n_sub in n_tmp :
			n_parent.attach(n_sub)
		del n_tmp
		return n_parent

