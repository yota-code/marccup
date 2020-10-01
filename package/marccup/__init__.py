#!/usr/bin/env python3

from marccup.parser.section import SectionParser
from marccup.parser.page import PageParser

import marccup.parser.libre as libre

def parse(pth) :
	if pth.is_dir() and pth / '__doc__.mcp' :
		# print(f"Document :: {pth}")
		pass
	
	if pth.is_file() :
		txt = pth.read_text()

		title_lst = list(libre.title_rec.finditer(txt))

		if len(title_lst) == 0 or ( len(title_lst) == 0 and txt.lstrip().startswith('= ') ) :
			# print(f"Section :: {pth}")
			return SectionParser().parse_section(txt)

		if lent(title_lst) > 1 :
			return PageParser().parse_page(txt)


