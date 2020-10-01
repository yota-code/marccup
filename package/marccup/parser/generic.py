#!/usr/bin/env python3

import hashlib

from cc_pathlib import Path

import oaktree
from oaktree.proxy.braket import BraketProxy

from marccup.parser.atom import Atom
from marccup.parser.libre import *

def find_all(txt, sub, offset=0) :
	sub_lst = list()
	i = txt.find(sub, 0)
	while i >= 0:
		sub_lst.append(i)
		i = txt.find(sub, i+1)
	return sub_lst

def jump_to_closing(txt) :
	d = 1
	for n, c in enumerate(txt) :
		if c == '<' :
			d += 1
		elif c == '>' :
			d -= 1
			if d == 0 :
				return n

def jump_to_closing_tag(txt, start) :
	d = 1
	n = start
	while True :
		c = txt[n]
		if c == '<'  :
			d += 1
		elif c == '>' :
			d -= 1
			if d == 0 :
				return n


def pick_higher(x_lst, p) :
	for x in x_lst :
		if p < x :
			return x
	return None

def trim_line(txt) :
	""" remove empty lines at the begining or at the end of a stack, in place """
	stack = txt.splitlines()
	while stack and not stack[0].strip() :
		stack.pop(0)
	while stack and not stack[-1].strip() :
		stack.pop(-1)
	return stack

class GenericParser() :

	# def __init__(self, debug_dir=None) :
	def __init__(self) :

		# self.debug_dir = debug_dir
		# if self.debug_dir is not None :
		# 	self.debug_dir.make_dirs()
		# self.debug_index = 0

		self.atom_map = dict()
		self.atom_index = 0

	def dbg(self, name, * value_lst) :
		return
		h = hashlib.blake2b(value_lst[0].encode('utf8')).hexdigest()[:8]
		if self.debug_dir is not None :
			pth = (self.debug_dir / f"{self.debug_index:02d}.{h}.{name}")
			pth.make_parents()
			pth.write_text(('\n' + '─' * 96 + '\n').join(str(value) for value in value_lst))
			self.debug_index += 1

	shortcut_lst = [
		['!!!', 'critical'],
		['!!', 'strong'],
		['!', 'em'],
		["'", 'code'],
		['"', 'quote'],
		['$', 'math'],
		['#', 'number'],
		['%', 'table'],
		['@', 'link'],
		['&', 'note'],
		['^', 'sup'],
		['_', 'sub'],
	]

	def clean_lines(self, txt) :
		# right trim each line
		lst = [ line.rstrip() for line in txt.splitlines() ]

		# remove empty lines at start or at the end
		while lst and not lst[0].strip() :
			lst.pop(0)
		while lst and not lst[-1].strip() :
			lst.pop(-1)
		txt = '\n'.join(lst)

		# format paragragraphs properly
		txt = paragraph_sep_rec.sub('\n\n', txt)

		return txt

	def expand_shortcut(self, txt) :
		# to do once for all on the initial text

		initial_txt = txt

		txt = txt.replace('\>', '&gt;')
		txt = txt.replace('\<', '&lt;')
		txt = txt.replace('\|', '&vert;')
		txt = txt.replace('\\\\', '&bsol;')

		for a, b in self.shortcut_lst :
			txt = txt.replace(a + '<', f'\\' + b + '<')

		self.dbg(f'expand_shortcut.txt', initial_txt, txt)

		return txt

	def protect_atom(self, txt) :
		""" on ne protège que le premier niveau, ça permet de ne garder que la structure générale du document """

		initial_txt = txt
		
		# first the triple blocks
		txt = self._to_atom(txt, block_rec, '>>>')

		# then the single ones
		txt = self._to_atom(txt, line_rec, '>')

		self.dbg(f"protect_atom.txt", initial_txt, txt, '\n'.join(f'{k} : {v}' for k, v in self.atom_map.items()))

		return txt

	def _to_atom(self, txt, start_rec, end_pattern) :

		start_lst = [(res.start(), res, 'start') for res in start_rec.finditer(txt)]
		end_lst = [(i, None, 'end') for i in find_all(txt, end_pattern)]

		marker_lst = sorted(start_lst + end_lst, key=(lambda x : x[0]))

		depth = 0
		prev = None
		match = None
		stack = list()
		for curs, res, value in marker_lst :
			if value == 'end' :
				depth -= 1
				if depth == 0 :
					self.atom_map[self.atom_index] = Atom(match, txt[match.end():curs])
					stack.append(f'\x02ATOM[{self.atom_index}]\x03')
					self.atom_index += 1
					prev = curs + len(end_pattern)
			else :
				depth += 1
				if depth == 1 :
					stack.append(txt[prev:curs])
					match = res
					prev = curs

		stack.append(txt[prev:])
		return ''.join(stack)

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

	def parse_title(self, section_txt) :
		""" parse a unique title at the beginning of a section """
		try :

			first_n = section_txt.index('\n')
			title_txt = section_txt[:first_n]
			title_res = title_rec.match(title_txt)
			if title_res is None :
				return section_txt, None
			
			return section_txt[first_n:].trim(), title_res

		except ValueError :
			return section_txt, None

		# if title_res is not None : #
		# 	o_section.grow('title', ident=title_res.group('ident')).add_text(title_res.group('title'))

	def parse(self, txt, automatic=False) :
		""" parse a text zone (no title) can be an alinea, a paragraph or a section """

		txt = self.expand_shortcut(txt)

		txt = self.protect_atom(txt)
		txt = self.clean_lines(txt)

		if '\n\n' in txt or not automatic :
			return self.parse_section(txt)
		elif '\n' in txt :
			return self.parse_paragraph(txt)
		else :
			return self.parse_alinea(txt)

	def _parse_section(self, txt, tag='section') :
		""" a section is a part of text which contains many paragraphs """

		initial_txt = txt

		o_section = oaktree.Leaf(tag)

		# protect higher level atoms and cleanup
		txt = self.protect_atom(txt)
		txt = self.clean_lines(txt)

		for paragraph_txt in txt.split('\n\n') :
			o_block = self.parse_paragraph(paragraph_txt)
			o_section.attach(o_block)
		
		self.dbg(f'GenericParser.parse_section.bkt', initial_txt, BraketProxy().save(o_section.root))

		return o_section

	def parse_paragraph(self, paragraph_txt) :
		""" 
		txt consists in, either :
			* some alineas
			* only one sole atom
			* a bullet list
		
		"""

		atom_block_res = atom_block_rec.match(paragraph_txt)
		if atom_block_res is not None :
			# the paragraph consists in a sole atom, with possibly an ident
			return self.parse_atom(atom_block_res, True)

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
					# the paragraph is just made of alineas
					# print("break")
					break
			else :
				# bullet !
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
		for res in atom_line_rec.finditer(txt) :
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
		elif atom.tag == "math" :
			if is_block :
				o_block = oaktree.Leaf('math', flag={'block'})
			else :
				o_block = oaktree.Leaf('math')
			o_block.add_text(atom.content[0].strip())
		else :
			o_block = self.parse_alinea('|'.join(atom.content), atom.tag)
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
