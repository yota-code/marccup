#!/usr/bin/env python3

import re

import oaktree
from oaktree.proxy.braket import BraketProxy

from cc_pathlib import Path


RAAAAAH

# alinea_ident_rec = re.compile(r'^\s*(?P<line>.*?)\s*#(?P<ident>[0-9]+)$')

DISABLED CODE (portable vers parser/generic.py)

shortcut_lst = [
	['!!!', 'critical'],
	['!!', 'important'],
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
		if c == '<' :
			d += 1
		elif c == '>' :
			d -= 1
			if d == 0 :
				return n

def find_all(txt, sub, offset=0) :
	sub_lst = list()
	i = txt.find(sub, 0)
	while i >= 0:
		sub_lst.append(i)
		i = txt.find(sub, i+1)
	return sub_lst

class Parser() :
	def __init__(self, debug_dir=Path('.marccup-tmp')) :
		self.debug_dir = debug_dir
		if self.debug_dir is not None :
			self.debug_dir.make_dirs()

	def clean_text(self, txt) :
		txt = '\n'.join(
			line.strip()
			for line in txt.strip().splitlines()
		)
		# if self.debug_dir :
		# 	(self.debug_dir / f"text_half_cleaned.txt").write_text(repr(txt))

		txt = paragraph_sep_rec.sub('\n\n', txt)

		# if self.debug_dir :
		# 	(self.debug_dir / f"text_twice_cleaned.txt").write_text(repr(txt))

		return txt.strip()

	def expand_shortcut(self, txt) :
		for a, b in shortcut_lst :
			txt = txt.replace(a + '<', f'\\' + b + '<')
			# if self.debug_dir :
			# 	(self.debug_dir / f"text_expanded_{b}.txt").write_text(txt)

		return txt

	def encode_atom(self, txt) :
		
		self.atom_map = dict()
		self.atom_index = 0

		txt = self._encode_atom(txt, block_rec, '>>>')
		txt = self._encode_atom(txt, line_rec, '>')

		if self.debug_dir :
			(self.debug_dir / "atom_map.json").save(self.atom_map)

		return txt, self.atom_map

	def _encode_atom(self, txt, start_rec, end_pattern) :
		start_res_lst = list(start_rec.finditer(txt))
		end_pattern_lst = find_all(txt, end_pattern)

		block_marker_lst = sorted(start_res_lst + end_pattern_lst, key=( lambda x : x if isinstance(x, int) else x.end() ))

		depth = 0
		cursor = None
		stack = list()
		o_space, o_tag = None, None
		for block_marker in block_marker_lst :
			if isinstance(block_marker, int) :
				depth -= 1
				if depth == 0 :
					self.atom_map[self.atom_index] = [o_space, o_tag, txt[cursor:block_marker]]
					cursor = block_marker + len(end_pattern)
					stack.append(f'\x01ATOM[{self.atom_index}]\x02')
					self.atom_index += 1
			else :
				depth += 1
				if depth == 1 :
					stack.append(txt[cursor:block_marker.start()])
					o_space, o_tag = block_marker.group('space'), block_marker.group('tag')
					cursor = block_marker.end()

		stack.append(txt[cursor:])

		return ''.join(stack)

	def decode_atom(self, txt, atom_map) :
		start, end = None, None
		stack = list()
		for atom_piece_res in atom_piece_rec.finditer(txt) :
			start = atom_piece_res.start()
			stack.append(txt[end:start])
			stack.append(atom_map[atom_piece_res.group('ident')])
			end = atom_piece_res.end()
		stack.append(txt[end:None])
		return ''.join(stack)
		
	def tst(self, txt) :
		txt = self.clean_text(txt)
		txt = self.expand_shortcut(txt)
		return self.encode_atom(txt)

	def parse_document(self, root_dir) :
		o_doc = oaktree.Leaf("doc")
		chapter_lst = [o_doc, None, None, None, None]
		for indent, section in (root_dir / "__doc__.tsv").load() :
			indent, section = int(indent), int(section)
			o_section = chapter_lst[indent - 1].grow('section')
			chapter_lst[indent] = o_section
			txt = (root_dir / f"{section}.bkt").read_text()
			self.parse_section(o_section, txt)
		return o_doc

	def parse_table(self, o_parent, txt) :
		o_table = o_parent.grow('table')
		for row in txt.split('---') :
			o_row = o_table.grow('table-row')
			for cell in row.split('|') :
				cell = cell.strip()

				# look for row or col span clues
				table_cell_span_res = table_cell_span_rec.match(cell)
				if table_cell_span_res is not None :
					row_n = table_cell_span_res.group('row_n')
					if row_n is not None :
						o_cell.nam["rspan"] = row_n
					col_n = table_cell_span_res.group('col_n')
					if col_n is not None :
						o_cell.nam["cspan"] = col_n
					cell = cell[table_cell_span_res.end():]

				# look for header clue
				if cell.startswith('=') :
					is_header = True
					cell = cell[1:].lstrip()
				else :
					is_header = False

				o_cell = self.parse_alinea(o_row, 'table-cell', cell)

				if is_header :
					o_cell.style.add('table-header')
		return o_table

	def parse_toc(self, toc_pth) :
		toc_item_rec = re.compile(r'^(?P<depth>=+)\s*(?P<title>.*?)\s*#(?P<ident>\d+)$')
		toc_lst = list()
		for line in toc_pth.read_text().splitlines() :
			res = toc_item_rec.match(line.strip())
			if res :
				toc_lst.append([len(res.group('depth')), res.group('title'), int(res.group('ident'))])
		return toc_lst

	def parse_splitblock(self, o_parent, toc_pth) :
		"""
		o_parent is a higher level container
		txt is a complete document which contains multiple section
		"""

		spec_dir = toc_pth.parent
		toc_lst = self.parse_toc(toc_pth)
		depth_lst = [o_parent,]
		for depth, title, ident in toc_lst :
			depth_lst = depth_lst[:depth]
			if depth == len(depth_lst) + 1 :
				o_section = depth_lst[-1].grow('section')
				depth_lst.append(o_section)
			self.parse_section(depth_lst[-1], (spec_dir / f"{ident:05d}.bkt").read_text())

	def parse_section(self, o_parent, txt) :
		""" une section peut contenir plusieurs paragraphes et éventuellement un titre"""

		# déroule les raccourcis
		txt = self.expand_shortcut(txt)

		if self.debug_dir :
			(self.debug_dir / "text_expanded.txt").write_text(txt)

		# nettoie un peu
		txt = self.clean_text(txt)

		if self.debug_dir :
			(self.debug_dir / "text_cleaned.txt").write_text(txt)

		# protège les balises de haut niveau
		txt, atom_map = self.encode_atom(txt)

		if self.debug_dir :
			(self.debug_dir / "atom_encode.txt").write_text(
				txt + '\n----\n' + '\n'.join(f'{k} : {v}' for k, v in atom_map.items())
			)

		# decoupe en lignes
		txt_lst = txt.split('\n')
		if txt.startswith('=') :
			# si la première ligne commence par '=', c'est le titre de section
			first_line = txt_lst.pop(0)
			title_line = first_line.lstrip('=').strip()
			self.parse_alinea(o_parent, title_line, 'title')

		# avec le reste, on nettoie un peu
		txt = '\n'.join(txt_lst).strip()
		# et on coupe par paragraphe
		for paragraph in txt.split('\n\n') :
			atom_block_res = atom_block_rec.match(paragraph)
			if atom_block_res is not None :
				space, tag, content = atom_map[int(atom_block_res.group('atom_n'))]
				if tag == "table" :
					o_block = self.parse_table(o_parent, content)
				else :
					o_block = self.parse_alinea(o_parent, tag, content.strip())
					o_block.flag.add('block')
				if atom_block_res.group('ident') is not None :
					o_block.ident = atom_block_res.group('ident').strip()
			else :
				for line in paragraph.splitlines() :
					if not bullet_list_rec.match(line) :
						o_paragraph = o_parent.grow('paragraph')
						self.parse_paragraph(o_paragraph, paragraph)
						break
				else :
					self.parse_bullet_list(o_parent, paragraph)
				
		if self.debug_dir :
			BraketProxy().save(o_parent.root, self.debug_dir / "atom_decode.bkt")

	def parse_paragraph(self, o_parent, txt) :
		for alinea in txt.split('\n') :
			self.parse_alinea(o_parent, 'alinea', alinea)

	def parse_bullet_list(self, o_parent, txt) :

		prev_indent = -1

		o_obj = o_parent
		for n, line in enumerate(txt.splitlines()) :
			res = bullet_list_rec.search(line)
			indent = len(res.group('tabs'))
			if indent == prev_indent :
				pass
			elif indent == prev_indent + 1 :
				if res.group('marker') == '*' :
					o_obj = o_obj.grow('ul')
				elif res.group('marker') == '#' :
					o_obj = o_obj.grow('ol')
			elif indent == prev_indent - 1 :
				o_obj = o_obj.parent
			self.parse_alinea(o_obj, 'li', res.group('line'))
			prev_indent = indent

	def parse_title(self, o_section, line) :
		""" specific function to parse the first line of a section """

		line = line.replace('\n', ' ')
		line = line.replace('\t', ' ')
		line = re.sub('\s+', ' ', line)

		line = line.lstrip('=').strip()

		o_title = o_section.grow('title')

		res = alinea_ident_rec.search(line)
		if res is not None :
			o_child.ident = res.group('ident')
			txt = txt[:res.start()]

		self._parse_content(o_child, txt)

		return o_child


	def parse_alinea(self, o_parent, txt, tag='alinea') :

		o_child = o_parent.grow(tag)

		res = alinea_ident_rec.search(txt)
		if res is not None :
			o_child.ident = res.group('ident')
			txt = txt[:res.start()]

		self._parse_content(o_child, txt)

		return o_child

	def _parse_content(self, o_parent, txt) :

		while True :
			line_res = line_rec.search(txt)

			if line_res is None :
				break

			o_parent.add_text(txt[:line_res.start()])

			content_start = line_res.end()
			content_len = jump_to_closing(txt[content_start:])

			o_child = o_parent.grow(line_res.group('tag'), space=line_res.group('space'))
			self._parse_content(o_child, txt[content_start:content_start + content_len])

			txt = txt[content_start+content_len+1:]

		o_parent.add_text(txt)

		




if __name__ == '__main__' :
#  	from oaktree.proxy.braket import BraketProxy

	u = Parser()
	u.encode_atom(Path('document/1005.bkt').read_text())

# 	# u.parse_text(p, "Maecenas \important<aliquam ligula id arcu> vestibulum, vitae auctor magna fermentum")
# 	#u.expand_shortcut(p, "Class \em<aptent taciti sociosqu> ad litora torquent per conubia \critical<nostra, per inceptos> himenaeos")
# 	p, m = u.tst("Nam volutpat, nisl at \\important<ornare elementum, massa \\sub<nibh> sollicitudin dui>, vitae ullamcorper nisl nibh id risus.")
# 	print(p)

# 	p = oaktree.Leaf("section")
# 	#.parse_section(Path('./1001.bkt').read_text())
# 	#BraketProxy().save(u, Path("1001.result.bkt"))
# 	#BraketProxy().save(p, Path("test.bkt"))