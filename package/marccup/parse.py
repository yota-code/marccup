#!/usr/bin/env python3

import re

import oaktree
from oaktree.proxy.braket import BraketProxy

from cc_pathlib import Path

alinea_ident_rec = re.compile(r'^\s*(?P<line>.*?)\s*#(?P<ident>[0-9]+)$')
paragraph_ident_rec = re.compile(r'^#(?P<ident>[0-9]+)$')
line_rec = re.compile(r'\\((?P<space>[a-z]+)\.)?(?P<tag>[a-z]+)<')

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

class Parser() :
	def __init__(self) :
		pass

	def expand_shortcut(self, txt) :
		for a, b in shortcut_lst :
			txt = txt.replace(f'{a}<', f'\\{b}<')
		Path("1001.expanded.bkt").write_text(txt)
		return txt
	
	def clean_lines(self, txt) :
		txt = '\n'.join(
			line.strip()
			for line in txt.strip().splitlines()
		)
		txt = paragraph_sep_rec.sub(txt, '\n\n')
		return txt.strip()

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

		txt_lst = txt.split('\n')
		if txt.startswith('=') :
			first_line = txt_lst.pop(0)
			o_parent.grow('title').add_text(first_line.lstrip('=').strip())

		txt = '\n'.join(txt_lst).strip()
		for paragraph in txt.split('\n\n') :
			o_paragraph = o_parent.grow('paragraph')
			for line in paragraph.split('\n') :
				res = paragraph_ident_rec.match(line)
				if res is None :
					res = alinea_ident_rec.match(line)
					if res is None :
						o_alinea = o_paragraph.grow('alinea')
					else :
						o_alinea = o_paragraph.grow('alinea', ident=int(res.group('ident')))
						line = res.group('line')
					self.parse_alinea(o_alinea, line)
				else :
					o_paragraph.ident = int(res.group('ident'))

	def parse_paragraph(self, txt) :
		pass

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
	# u.parse_text(p, "Class \em<aptent taciti sociosqu> ad litora torquent per conubia \critical<nostra, per inceptos> himenaeos")
	u.parse_alinea(p, "Nam volutpat, nisl at \\important<ornare elementum, massa \\sub<nibh> sollicitudin dui>, vitae ullamcorper nisl nibh id risus.")

	BraketProxy().save(p, Path("test.bkt"))