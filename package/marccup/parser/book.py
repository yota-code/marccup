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
	def __init__(self) :

		self.atom_map = dict()
		self.atom_index = 0

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

	def parse_index(self, txt) :

		index_lst = list()

		line_lst = txt.splitlines()
		num = [0,]
		prev_depth = 1
		for n, line in enumerate(line_lst) :
			if not line.strip() :
				continue
			title_res = title_rec.match(line)
			if title_res is None :
				print(f"error processing index line {n+1}")
				continue
			
			depth = len(title_res.group('depth'))
			title = title_res.group('title')
			ident = int(title_res.group('ident'))

			if depth <= prev_depth + 1 :
				if depth == prev_depth + 1 :
					num += [0,]
				num = num[:depth]
				num[-1] += 1
			else :
				raise ValueError()

			index_lst.append([tuple(num), title, ident])

			prev_depth = depth
	
		return index_lst

	def parse_refer(self, txt) :

		txt = self.expand_shortcut(txt)

		txt = self.protect_atom(txt)
		txt = self.clean_lines(txt)

		print(txt)

		
	# def parse_index(self) :

	# 	self.index_lst = list()

	# 	line_lst = (self.base_dir / "index").read_text().splitlines()
	# 	num = [0,]
	# 	prev_depth = 1
	# 	for n, line in enumerate(line_lst) :
	# 		if not line.strip() :
	# 			continue
	# 		title_res = title_rec.match(line)
	# 		if title_res is None :
	# 			print(f"error processing index line {n+1}")
	# 			continue
	# 		depth = len(title_res.group('depth'))
	# 		title = title_res.group('title')
	# 		ident = int(title_res.group('ident'))

	# 		self.index_lst.append([depth, title, ident])

	def _check_index(self) :
		# mettre plein de vérification de cohérence, ici
		pass
