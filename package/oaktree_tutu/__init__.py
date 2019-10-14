#!/usr/bin/env python3

import importlib
import copy

TREE = 0
CONTAINER = 1
INLINE = 2

from .line import Line
from .leaf import Leaf, Select

class Text() :
	def __init__(self, ref, start=None, end=None) :
		#dbg("Text( {0} )".format(line[start:end]))
		self.ref = ref
		self.start = start
		self.end = end
		
	def __str__(self) :
		return self.ref[self.start:self.end]

