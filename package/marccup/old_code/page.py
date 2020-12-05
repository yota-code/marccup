#!/usr/bin/env python3

""" page parser, a page is a self containing document, with title, sections, and everyting in a single file"""

import re

import oaktree

from marccup.parser.generic import GenericParser
from marccup.parser.libre import *

""" on devrait avoir la logique qu'un parser retourne un objet, sans se soucier de savoir où il est attaché,
mais ça pose un problème avec les alineas qui pourraient potentiellement ne pas être attachés tel quel...

"""

class PageParser(GenericParser) :

	def parse_page(self, txt) :
		o_page = oaktree.Leaf('page')

		prev_depth = 0
		prev_node = o_page

		prev_res = None
		stack = list()

		for line in txt.splitlines() :
			title_res = title_rec.match(line)
			if title_res is None :
				# push the line on the stack
				stack.append(line)
			else :
				if prev_res is None : # no title previously found, this must be some introductory text
					o_section = self.parse_section('\n'.join(stack))
					prev_node.attach(o_section)
				else :
					o_section = self.parse_section('\n'.join(stack), prev_res)
					depth = len(prev_res.group('depth'))

					if prev_depth + 1 < depth :
						raise ValueError

					curr_node = prev_node.ancestor_lst[depth-1]
					curr_node.attach(o_section)

					prev_depth = depth
					prev_node = o_section

				prev_res = title_res
				stack = [line,]

		return o_page
