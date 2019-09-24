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
	['!', 'emphasized'],
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

	def parse(self, pth) :
		txt = pth.read_text()

		txt = self.expand_shortcut(txt)
		txt = self.clean_lines(txt)

		o_section = oaktree.Leaf('section', ident=int(pth.stem))

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
						o_paragraph.grow('alinea', ident=int(res.group('ident'))).add_text(line)
				else :
					o_paragraph.ident = int(res.group('ident'))

		return o_section

if __name__ == '__main__' :
	u = Parser().parse(Path('./1001.bkt'))
	BraketProxy().save(u, Path("1001.result.bkt"))