#!/usr/bin/env python3

import re

import oaktree
from oaktree.proxy.braket import BraketProxy

from cc_pathlib import Path

alinea_ident_rec = re.compile('^\s*(?P<line>.*?)\s*#(?P<ident>[0-9]+)$')
paragraph_ident_rec = re.compile('^#(?P<ident>[0-9]+)$')

paragraph_rec = re.compile('\n\n+')

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
		txt = paragraph_rec.sub(txt, '\n\n')
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

	def parse_text(self, o_parent, txt, start=0) :
		print('---', txt[start:])
		m = 0 # text, tag or content mode
		d = 0 # depth
		tag_start, tag_stop = None, None
		content_start, content_stop = None, None
		for n, c in enumerate(txt[start:]) :
			if m == 0 and c == '\\' :
				m = 1
				tag_start = n+1
				#d = 0
			elif m == 1 and c == '<' :
				m = 2
				d += 1
				print(d, 'A+', n, c)
				tag_stop = n
				content_start = n+1
			elif m == 2 :
				if c == '<' :
					d += 1
					print(d, 'B+', n, c)
				elif c == '>' :
					d -= 1
					print(d, 'C-', n, c)
					if d == 0 :
						m = 0
						content_stop = n
						print(tag_start, tag_stop, txt[tag_start:tag_stop])
						print(content_start, content_stop, txt[content_start:content_stop])
						tag_start, tag_stop = None, None
						content_start, content_stop = None, None


		




if __name__ == '__main__' :
	u = Parser()
	#.parse_section(Path('./1001.bkt').read_text())
	#BraketProxy().save(u, Path("1001.result.bkt"))
	u.parse_text(None, "Maecenas \important<aliquam ligula id arcu> vestibulum, vitae auctor magna fermentum")
	u.parse_text(None, "Class \em<aptent taciti sociosqu> ad litora torquent per conubia \critical<nostra, per inceptos> himenaeos")
	u.parse_text(None, "Nam volutpat, nisl at \important<ornare elementum, massa \sub<nibh> sollicitudin dui>, vitae ullamcorper nisl nibh id risus.")