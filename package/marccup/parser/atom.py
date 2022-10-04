#!/usr/bin/env python3

import oaktree

from marccup.parser.libre import *

class Atom(oaktree.Leaf) :
	"""
un atom c'est un tag un peu particulier, d'accès rapide et sans descendant ?

\space.tag<content|pos1|pos2|key1=nam1|!flag1'>

le premier champ est du contenu, le reste c'est des paramètres divers
	"""

	def pack(self, res, txt) :
		self.space = res.group('space')
		self.tag = res.group('tag')

		self.is_block = len(res.group('marker')) == 3

		self.content = txt

		return self

	def parse(self, res, txt) :

		self.space = res.group('space')
		self.tag = res.group('tag')
	
		self.pos = list()
		self.nam = dict()
		self.flag = set()
		self.style = set()

		self.is_block = len(res.group('marker')) == 3

		item_lst = txt.split('|')
		self.sub = [item_lst.pop(0),]

		arg_lst = list()
		for item in item_lst :
			item = item.strip()
			if item.startswith('!') :
				self.flag.add(item[1:].strip())
			elif item.startswith('@') :
				self.style.add(item[1:].strip())
			elif '=' in item :
				key, null, value = item.partition('=')
				self.nam[key.strip()] = value.strip()
			else :
				self.pos.append(item.strip())

		print(self)

		return self
			
	def __str__(self) :
		space = '' if self.space is None else f'{self.space}.'

		n = 3 if self.is_block else 1

		item_lst = self.sub + self.pos
		for key, value in self.nam.items() :
			item_lst.append(f'{key}={value}')
		for flag in self.flag :
			item_lst.append(f'!{flag}')
		for style in self.style :
			item_lst.append(f'@{style}')

		return f"\\{space}{self.tag}{'<'*n}{'|'.join(item_lst)}{'>'*n}"


class AtomParser() :

	shortcut_lst = [
		['!!!', 'critical'],
		['!!', 'important'],
		['!', 'strong'],
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

	""" deal with chunk of text and focus on the handling of atoms """
	def __init__(self, debug_dir=None) :
		self.debug_dir = debug_dir

		self.atom_map = dict()
		self.atom_index = 0

	def clean(self, txt) :

		txt = self.expand(txt)
		txt = self.protect(txt)

		# right trim each line
		lst = [ line.rstrip() for line in txt.splitlines() ]

		# remove empty lines at start or at the end of the section
		while lst and not lst[0].strip() :
			lst.pop(0)
		while lst and not lst[-1].strip() :
			lst.pop(-1)
		txt = '\n'.join(lst)

		# format paragragraphs properly
		txt = paragraph_sep_rec.sub('\n\n', txt)

		return txt

	def parse(self, atom, o_parent=None, is_block=False) :

		atom_n = int(atom['atom_n'])

		ident = atom.get('ident', None)
		if ident is not None :
			ident = int(ident)

		space, tag, txt = self.atom_map[atom_n]

		try :
			m = getattr(self, f'_parse__{tag}' if space is None else f'_parse_{space}_{tag}')
		except :
			m = self._parse__default__

		o_atom = oaktree.Leaf(tag, ident, space, parent=o_parent)
		if is_block :
			o_atom.flag.add('is_block')

		m(txt, o_atom)
			
		return o_atom

	def _parse__default__(self, txt, o_atom) :
		# if self.debug_dir is not None :
		# 	print(f'AtomParser._parse__default__({txt[:32]}..., {o_atom.header()})')

		item_lst = txt.split('|')
		o_atom.sub = [item_lst.pop(0),]

		arg_lst = list()
		for item in item_lst :
			item = item.strip()
			if item.startswith('!') :
				o_atom.flag.add(item[1:].strip())
			elif item.startswith('@') :
				o_atom.style.add(item[1:].strip())
			elif '=' in item :
				key, null, value = item.partition('=')
				o_atom.nam[key.strip()] = value.strip()
			else :
				o_atom.pos.append(item.strip())

	def expand(self, txt) :

		# to do once for all on the raw text
		txt = txt.replace('\>', '&gt;')
		txt = txt.replace('\<', '&lt;')
		txt = txt.replace('\|', '&vert;')
		txt = txt.replace('\\\\', '&bsol;')

		for a, b in self.shortcut_lst :
			txt = txt.replace(a + '<', f'\\' + b + '<')

		return txt

	def protect(self, txt) :
		""" return a txt where:
			* first level atoms are replaced by placeholders
			* their content is saved in a dict
		"""
		txt = self._scan(txt, 3)
		txt = self._scan(txt, 1)

		return txt

	def _scan(self, txt, marker_len) :
		open_rec = re.compile(r'\\((?P<space>[a-z]+)\.)?(?P<tag>[a-z_]+)(?P<m_open>' + ('<' * marker_len) + r')')
		close_rec = re.compile(r'(?P<m_close>' + ('>' * marker_len) + r')')

		open_lst = [(res.start(), res, 'open') for res in open_rec.finditer(txt)]
		close_lst = [(res.end(), res, 'close') for res in close_rec.finditer(txt)]

		print(open_lst)
		print(close_lst)

		marker_lst = sorted(open_lst + close_lst, key=(lambda x : x[0]))

		depth = 0
		prev = None
		open_res = None
		stack = list()
		for curs, res, value in marker_lst :
			print(curs, res, value, depth)
			if value == 'close' :
				depth -= 1
				if depth == 0 :
					close_res = res
					self.atom_map[self.atom_index] = (
						open_res.group('space'),
						open_res.group('tag'),
						txt[open_res.end():close_res.start()]
					)
					stack.append(f'\x02ATOM[{self.atom_index}]\x03')
					self.atom_index += 1
					prev = close_res.end()
			else :
				depth += 1
				if depth == 1 :
					open_res = res
					stack.append(txt[prev:curs])
					prev = curs
		stack.append(txt[prev:])

		return ''.join(stack)

	def _parse_table(self, o_atom, txt) :

		# a bit of cleaning, such as the row separator is really the sole marker on its line
		txt = '\n'.join(
			( line.strip() if table_split_rec.match(line) is not None else line )
			for line in '|'.join(txt).splitlines()
		)

		txt = self.protect(txt)

		if table_split_rec.search(txt) is not None :
			row_lst = table_split_rec.split(txt)
		else :
			row_lst = [ line for line in txt.splitlines() if line.strip() ]

		for row in row_lst :
			o_row = o_atom.grow('table_row')
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

	def _parse__img(self, txt, o_atom) :
		if '\n' in txt :
			o_atom.tag = 'gallery'
			for line in txt.strip().splitlines() :
				url, null, alt = line.strip().partition('|')
				o_img = o_atom.grow('img', pos=[url,])
				if alt.strip() :
					o_img.add_text(alt.strip())
		else :
			url, null, alt = txt.strip().partition('|')
			o_atom.pos = [url,]
			if alt.strip() :
				o_atom.add_text(alt.strip())

