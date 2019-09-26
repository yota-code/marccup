#!/usr/bin/env python3

import re

import oaktree
from oaktree.proxy.braket import BraketProxy

from cc_pathlib import Path

alinea_ident_rec = re.compile('^\s*(?P<line>.*?)\s*#(?P<ident>[0-9]+)$')
paragraph_ident_rec = re.compile('^#(?P<ident>[0-9]+)$')
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

	def parse_section(self, txt) :

		txt = self.expand_shortcut(txt)
		txt = self.clean_lines(txt)

		# o_section = oaktree.Leaf('section', ident=int(pth.stem))
		o_section = oaktree.Leaf('section')

		txt_lst = txt.split('\n')
		if txt.startswith('=') :
			first_line = txt_lst.pop(0)
			o_section.grow('title').add_text(first_line.lstrip('=').strip())

		txt = '\n'.join(txt_lst)
		for paragraph in txt.split('\n\n') :
			o_paragraph = o_section.grow('paragraph')
			for line in paragraph.split('\n') :
				res = paragraph_ident_rec.match(line)
				if res is None :
					res = alinea_ident_rec.match(line)
					if res is None :
						o_paragraph.grow('alinea').add_text(line)
					else :
						o_paragraph.grow('alinea', ident=int(res.group('ident'))).add_text(res.group('line'))
				else :
					o_paragraph.ident = int(res.group('ident'))

		return o_section

	def parse_paragraph(self, txt) :
		pass

	def parse_text(self, o_parent, txt) :
		while True :
			line_res = line_rec.search(txt)

			if line_res is None :
				break

			o_parent.add_text(txt[:line_res.start()])

			content_start = line_res.end()
			content_len = jump_to_closing(txt[content_start:])

			o_child = o_parent.grow(line_res.group('tag'), space=line_res.group('space'))
			self.parse_text(o_child, txt[content_start:content_start + content_len])

			txt = txt[content_start+content_len+1:]

		o_parent.add_text(txt)

		




if __name__ == '__main__' :
	from oaktree.proxy.braket import BraketProxy

	u = Parser()

	p = oaktree.Leaf("bu")
	#.parse_section(Path('./1001.bkt').read_text())
	#BraketProxy().save(u, Path("1001.result.bkt"))
	# u.parse_text(p, "Maecenas \important<aliquam ligula id arcu> vestibulum, vitae auctor magna fermentum")
	# u.parse_text(p, "Class \em<aptent taciti sociosqu> ad litora torquent per conubia \critical<nostra, per inceptos> himenaeos")
	u.parse_text(p, "Nam volutpat, nisl at \important<ornare elementum, massa \sub<nibh> sollicitudin dui>, vitae ullamcorper nisl nibh id risus.")

	BraketProxy().save(p, Path("test.bkt"))