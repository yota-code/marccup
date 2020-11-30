#!/usr/bin/env python3

import datetime

import oaktree

import oaktree.proxy.braket

from marccup.parser.generic import GenericParser
from marccup.parser.libre import *

def todo(dst, * src_lst) :
	if not dst.is_file() :
		return True

	dst_time = dst.stat().st_mtime
	for src in src_lst :
		if src.stat().st_mtime >= dst_time :
			return True
	
	return False
	
class BookParser(GenericParser) :

	def parse_book(self, base_dir) :

		self.parse_index(base_dir)

		(base_dir / "parsed_index.tsv").save(index)

		self._check_index(index)

		o_book = oaktree.Leaf('book')

		prev_depth = 0
		prev_node = o_book

		for num, title, ident in index :
			depth = len(num)

			txt = (base_dir / "part" / f'{ident:04d}').read_text()
			mcp = self.expand_shortcut(txt)

			o_section = self.parse_section(mcp)
			o_title = oaktree.Leaf('title').add_text(title if title != '~' else '')

			sub_lst = o_section.sub
			o_section.sub = list()
			o_section.attach(o_title, * sub_lst)

			curr_node = prev_node.ancestor_lst[depth-1]
			curr_node.attach(o_section)

			prev_depth = depth
			prev_node = o_section

		return o_book

