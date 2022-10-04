#!/usr/bin/env python3

import hashlib

from cc_pathlib import Path

import oaktree

from oaktree.proxy.braket import BraketProxy

from marccup.parser.atom import Atom

from marccup.parser.common import *
from marccup.parser.libre import *

class GenericParser() :

	# def __init__(self, debug_dir=None) :
	def __init__(self, debug_dir=None) :

		self.debug_dir = debug_dir
		if self.debug_dir is not None :
			self.debug_dir.make_dirs()
		self.debug_index = 0

		self.atom_map = dict()
		self.atom_index = 0

	def dbg(self, name, * value_lst) :

		if self.debug_dir is None :
			return
			
		h = hashlib.blake2b(value_lst[0].encode('utf8')).hexdigest()[:8]
		if self.debug_dir is not None :
			pth = (self.debug_dir / f"{self.debug_index:02d}.{h}.{name}")
			pth.make_parents()
			pth.write_text(('\n' + '─' * 96 + '\n').join(str(value) for value in value_lst))
			self.debug_index += 1


	def clean_lines(self, txt) :
		# right trim each line
		lst = [ line.rstrip() for line in txt.splitlines() ]

		# remove empty lines at start or at the end of the block
		while lst and not lst[0].strip() :
			lst.pop(0)
		while lst and not lst[-1].strip() :
			lst.pop(-1)
		txt = '\n'.join(lst)

		# format paragragraphs properly
		txt = paragraph_sep_rec.sub('\n\n', txt)

		return txt





	def restore_atom(self, txt) :
		start, end = None, None
		stack = list()
		for atom_piece_res in atom_piece_rec.finditer(txt) :
			start = atom_piece_res.start()
			stack.append(txt[end:start])
			stack.append(str(self.atom_map[int(atom_piece_res.group('ident'))]))
			end = atom_piece_res.end()
		stack.append(txt[end:None])
		return ''.join(stack)

	def parse(self, txt) :
		""" parse a text zone (no title) can be an alinea, a paragraph or a section (many paragraph)"""

		txt = self.expand_shortcut(txt)

		txt = self.protect_atom(txt)

		txt = self.clean_lines(txt)

		if '\n\n' in txt :
			return self._parse_section(txt)
		elif '\n' in txt :
			return self.parse_paragraph(txt)
		else :
			return self.parse_alinea(txt)

	def extract_title(self, txt) :
		""" parse a unique title at the beginning of a section """

		line_lst = txt.splitlines()
		title_res = title_rec.match(line_lst[0])
		if title_res is not None :
			o_title = oaktree.Leaf('title')
			o_title.nam['depth'] = len(title_res.group('depth'))
			if title_res.group('ident') is not None :
				o_title.ident = int(title_res.group('ident'))
			return line_lst[1:], title_res
		return txt, None

		# if title_res is not None : #
		# 	o_section.grow('title', ident=title_res.group('ident')).add_text(title_res.group('title'))


	def _parse_section(self, txt, tag='section') :
		""" a section is a part of text which contains many paragraphs but no title """

		initial_txt = txt

		o_section = oaktree.Leaf(tag)

		# protect higher level atoms and cleanup
		txt = self.protect_atom(txt)
		txt = self.clean_lines(txt)

		# le titre devrait être lu ailleurs non ? mais je sais vraiment pas où...
		# line_lst = txt.splitlines()
		# title_res = title_rec.match(line_lst[0])
		# if title_res is not None :
		# 	o_section.nam['depth'] = len(title_res.group('depth'))
		# 	if title_res.group('ident') is not None :
		# 		o_section.ident = int(title_res.group('ident'))
		# 	o_section.grow('title').add_text(title_res.group('title'))
		# 	txt = '\n'.join(line_lst[1:]).strip()

		for paragraph_txt in txt.split('\n\n') :
			o_block = self.parse_paragraph(paragraph_txt)
			o_section.attach(o_block)
		
		# self.dbg(f'GenericParser.parse_section.bkt', initial_txt, BraketProxy().save(o_section.root))

		return o_section

	def parse_paragraph(self, paragraph_txt) :
		""" 
		txt consists in, either :

			* some alineas
			* a single atom
			* a bullet list
		
		"""

		print(f"parse_paragraph({paragraph_txt[:24]}...)")

		atom_block_res = atom_packb_rec.match(paragraph_txt)
		if atom_block_res is not None :
			# the paragraph consists in a sole atom, with possibly an ident
			u = self.parse_atom(atom_block_res, True)
			print("PRROUUUT", u)
			return u

			# atom = self.atom_map[int(atom_block_res.group('atom_n'))]
			# if atom.tag == "table" :
			# 	o_block = self.parse_table(atom.content)
			# elif atom.tag == "math" :
			# 	# easy, let's do it now
			# 	o_block = oaktree.Leaf('math', flag={'block'}).add_text(atom.content[0].strip())
			# else :
			# 	o_block = self.parse_alinea('|'.join(atom.content), atom.tag)
			# 	o_block.flag.add('block')

			# if atom_block_res.group('ident') is not None :
			# 	o_block.ident = atom_block_res.group('ident').strip()

			# return o_block

		else :
			# the paragraph is made of alineas, bullet or normal
			for alinea_txt in paragraph_txt.splitlines() :
				# print(alinea_txt)
				# let's check that is is a not a bullet of numbered list
				if not bullet_list_rec.match(alinea_txt) :
					# there is one normal alinea inside, not a bullet list
					break
			else :
				# only bullets ! let's parse it
				return self.parse_list(paragraph_txt)
			
		# no bullet
		o_block = oaktree.Leaf('paragraph')
		alinea_lst = paragraph_txt.splitlines()

		# if the last line is a paragraph ident, parse it, and pop it
		res = paragraph_ident_rec.match(alinea_lst[-1])
		if res is not None :
			o_block.ident = int(res.group('ident'))
			alinea_lst.pop(-1)

		for alinea_txt in alinea_lst :
			o_line = self.parse_alinea(alinea_txt)
			o_block.attach(o_line)

		return o_block

	def parse_list(self, txt) :

		prev_indent = -1

		o_root = None
		for n, line in enumerate(txt.splitlines()) :

			res = bullet_list_rec.search(line)
			indent = len(res.group('tabs'))

			to_grow = False
			if indent == prev_indent :
				# same level, nothing to add, o_list should exists
				pass
			elif indent == prev_indent + 1 :
				# new indentation level, will create a new ol/ul group
				to_grow = True
			elif indent < prev_indent :
				# reduced indentation level
				o_list = o_list.parent_n(2 * (prev_indent - indent))
			else :
				# on rattrappe l'indentation si le premier est également indenté ( ce qui n'est pas très standard )
				to_grow = True

			if to_grow :
				if res.group('marker') == '*' :
					o_list = oaktree.Leaf('ul')
				elif res.group('marker') == '#' :
					o_list = oaktree.Leaf('ol')
				else :
					raise ValueError()
				if o_root is None :
					o_root = o_list
				else :
					o_alinea.attach(o_list)

			o_alinea = self.parse_alinea(res.group('line'), 'li')

			o_list.attach(o_alinea)

			prev_indent = indent

		return o_root

	def parse_alinea(self, txt, tag='alinea') :
		"""
		txt: should not contain any line feed
		tag: can be something else than 'alinea'. most of the time it will be 'li'
		"""

		o_alinea = oaktree.Leaf(tag)

		res = alinea_ident_rec.search(txt)
		if res is not None :
			# if the alinea ident exists, parse it and cut it
			o_alinea.ident = int(res.group('ident'))
			txt = txt[:res.start()]

		txt = txt.rstrip()

		# the first level atoms have already been parsed
		prev = None
		for res in atom_packl_rec.finditer(txt) :
			curr = res.start()
			s = txt[prev:curr]
			if s.strip() :
				o_alinea.add_text(s)
			o_atom = self.parse_atom(res, False)
			o_alinea.attach(o_atom)
			prev = res.end()
		s = txt[prev:None]
		if s.strip() :
			o_alinea.add_text(s)

		return o_alinea

	def parse_atom(self, atom_res, is_block) :

		# the paragraph consists in a sole atom, with possibly an ident
		atom = self.atom_map[int(atom_res.group('atom_n'))]
		if atom.tag == "table" :
			o_block = self._parse_atom_table(atom.content)
		elif atom.tag.startswith("high_") :
			o_block = self.parse_alinea('|'.join(atom.content), atom.tag)
			o_block.pos.append(int(atom.tag[5:]))
		elif atom.tag == "math" :
			if is_block :
				o_block = oaktree.Leaf('math', flag={'block'})
			else :
				o_block = oaktree.Leaf('math')
			o_block.add_text(atom.content[0].strip())
		else :
			o_block = self.parse_alinea('|'.join(atom.sub), atom.tag)
			if len(atom.sub) == 1 and '\n' in atom.sub[0] :
				o_block.flag.add('block')

		if is_block and atom_res.group('ident') is not None :
			o_block.ident = int(atom_res.group('ident').strip())

		return o_block

	# def _parse_atom(self, atom) :
	# 	o_atom = oaktree.Leaf(atom.tag)
	# 	o_atom.add_text('|'.join(atom.content))
	# 	return o_atom


	# def _parse_content(self, o_parent, txt) :
	# 	""" reccursive content parsing, here no title, no paragraphe, no line break, just content """

	# 	while True :
	# 		line_res = line_rec.search(txt)

	# 		if line_res is None :
	# 			break

	# 		o_parent.add_text(txt[:line_res.start()])

	# 		content_start = line_res.end()
	# 		content_len = jump_to_closing(txt[content_start:])

	# 		o_child = o_parent.grow(line_res.group('tag'), space=line_res.group('space'))
	# 		self._parse_content(o_child, txt[content_start:content_start + content_len])

	# 		txt = txt[content_start+content_len+1:]

	# 	o_parent.add_text(txt)


	def _parse_atom_table(self, txt) :

		o_table = oaktree.Leaf('table')

		# a bit of cleaning, such as the row separator is really the sole marker on its line
		txt = '\n'.join(
			( line.strip() if table_split_rec.match(line) is not None else line )
			for line in '|'.join(txt).splitlines()
		)

		txt = self.protect_atom(txt)

		if table_split_rec.search(txt) is not None :
			row_lst = table_split_rec.split(txt)
		else :
			row_lst = [ line for line in txt.splitlines() if line.strip() ]


		for row in row_lst :
			o_row = o_table.grow('table_row')
			for cell in row.split('|') :

				cell = cell.strip()

				# look for row or col span clues
				table_span_res = table_span_rec.match(cell)
				if table_span_res is not None :
					row_n = table_span_res.group('row_n')
					if row_n is not None :
						o_cell.nam["rspan"] = row_n
					col_n = table_span_res.group('col_n')
					if col_n is not None :
						o_cell.nam["cspan"] = col_n
					cell = cell[table_span_res.end():]

				# look for header clue
				if cell.startswith('=') :
					is_header = True
					cell = cell[1:].lstrip()
				else :
					is_header = False

				o_cell = o_row.grow('table_cell')

				o_content = self.parse(cell, True)
				o_cell.attach(* o_content.sub)

				if is_header :
					o_cell.flag.add('header')

		return o_table
