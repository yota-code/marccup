#!/usr/bin/env python3

import re

import oaktree
from oaktree.proxy.braket import BraketProxy

from cc_pathlib import Path

alinea_ident_rec = re.compile(r'^\s*(?P<line>.*?)\s*#(?P<ident>[0-9]+)$')
paragraph_ident_rec = re.compile(r'^#(?P<ident>[0-9]+)$')

line_rec = re.compile(r'\\((?P<space>[a-z]+)\.)?(?P<tag>[a-z]+)<')

atom_piece_rec = re.compile(r'<__atom\[(?P<ident>\d+)\]__>')

paragraph_sep_rec = re.compile('\n\n+')

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

class Parser() :
	def __init__(self, debug_dir=None) :
		self.debug_dir = debug_dir

	def clean_lines(self, txt) :
		txt = '\n'.join(
			line.strip()
			for line in txt.strip().splitlines()
		)
		txt = paragraph_sep_rec.sub(txt, '\n\n')
		return txt.strip()

	def expand_shortcut(self, txt) :
		for a, b in shortcut_lst :
			txt = txt.replace(f'{a}<', f'\\{b}<')
		Path("1001.expanded.bkt").write_text(txt)
		return txt

	def encode_atom(self, txt) :
		""" the atoms are only the higher level of an item, they must be protected first """

		result_lst = list()
		atom_map = dict()

		mode = 0
		depth = 0
		atom_i = 0
		atom_end = None
		for n, c in enumerate(txt) :
			if mode == 0 and c == '\\' :
				atom_start = n+1
				mode = 1
				result_lst.append(txt[atom_end:atom_start-1])
			elif mode == 1 and c == '<' :
				depth += 1
				mode = 2
				atom_sep = n+1
			elif mode == 2 :
				if c == '<' :
					depth += 1
				elif c == '>' :
					depth -= 1
					if depth == 0 :
						atom_end = n+1
						atom_map[atom_i] = [txt[atom_start:atom_sep-1], txt[atom_sep:atom_end-1]]
						result_lst.append(f"<__atom[{atom_i}]__>")
						atom_i += 1
						mode = 0
		result_lst.append(txt[atom_end:None])

		return ''.join(result_lst), atom_map

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
		txt = self.clean_lines(txt)
		txt = self.expand_shortcut(txt)
		return self.encode_atom(txt)
		# while True :
		# 	atom_header_res = atom_header_rec.search(txt)

		# 	if atom_header_res is None :
		# 		break

		# 	result_lst.append(txt[:atom_header_res.start()])

		# 	atom_start = atom_header_res.end()
		# 	atom_len = jump_to_closing_tag(txt, atom_start)

		# 	o_child = o_parent.grow(atom_header_res.group('tag'), space=atom_header_res.group('space'))
		# 	self.parse_alinea(o_child, txt[content_start:content_start + content_len])

		# 	txt = txt[content_start+content_len+1:]

		# o_parent.add_text(txt)

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

	def parse_section(self, o_parent, txt) :

		txt = self.expand_shortcut(txt)
		txt = self.clean_lines(txt)

		txt, atom_map = self.encode_atom(txt)

		if self.debug_dir :
			(self.debug_dir / "atom_encode.txt").write_text(
				txt + '\n----\n' + '\n'.join(f'{k} : {v}' for k, v in atom_map.items())
			)

		txt_lst = txt.split('\n')
		if txt.startswith('=') :
			first_line = txt_lst.pop(0)
			o_parent.grow('title').add_text(first_line.lstrip('=').strip())

		txt = '\n'.join(txt_lst).strip()
		for paragraph in txt.split('\n\n') :
			atom_piece_res = atom_piece_rec.match(paragraph)
			if atom_piece_res is not None :
				tag, content = atom_map[int(atom_piece_res.group('ident'))]
				if tag == "table" :
					self.parse_table(o_parent, content)
				else :
					o_block = o_parent.grow(tag, flag=['block',])
					self.parse_alinea(o_block, content)
			else :
				o_paragraph = o_parent.grow('paragraph')
				self.parse_paragraph(o_paragraph, paragraph)

		if self.debug_dir :
			BraketProxy().save(o_parent.root, self.debug_dir / "atom_decode.bkt")

	def parse_paragraph(self, o_parent, txt) :
		for alinea in txt.split('\n') :
			res = paragraph_ident_rec.match(alinea)
			if res is None :
				res = alinea_ident_rec.match(alinea)
				if res is None :
					o_alinea = o_parent.grow('alinea')
				else :
					o_alinea = o_parent.grow('alinea', ident=int(res.group('ident')))
					line = res.group('line')
				self.parse_alinea(o_alinea, alinea)
			else :
				o_parent.ident = int(res.group('ident'))

	def parse_alinea(self, o_parent, txt) :
		while True :
			line_res = line_rec.search(txt)

			if line_res is None :
				break

			o_parent.add_text(txt[:line_res.start()])

			content_start = line_res.end()
			content_len = jump_to_closing(txt[content_start:])

			o_child = o_parent.grow(line_res.group('tag'), space=line_res.group('space'))
			self.parse_alinea(o_child, txt[content_start:content_start + content_len])

			txt = txt[content_start+content_len+1:]

		o_parent.add_text(txt)

		




if __name__ == '__main__' :
	from oaktree.proxy.braket import BraketProxy

	u = Parser()

	p = oaktree.Leaf("alinea")
	#.parse_section(Path('./1001.bkt').read_text())
	#BraketProxy().save(u, Path("1001.result.bkt"))
	# u.parse_text(p, "Maecenas \important<aliquam ligula id arcu> vestibulum, vitae auctor magna fermentum")
	#u.expand_shortcut(p, "Class \em<aptent taciti sociosqu> ad litora torquent per conubia \critical<nostra, per inceptos> himenaeos")
	p, m = u.tst("Nam volutpat, nisl at \\important<ornare elementum, massa \\sub<nibh> sollicitudin dui>, vitae ullamcorper nisl nibh id risus.")
	print(p)
	#BraketProxy().save(p, Path("test.bkt"))