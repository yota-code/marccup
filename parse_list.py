#!/usr/bin/env python3

import re
import sys

from pathlib import Path

import doctree

txt = [i.rstrip() for i in Path(sys.argv[1]).read_text().splitlines()]


rec = re.compile(r'^(?P<tab>\t*)(?P<marker>[\*#]) (?P<line>.*)$')

prev_indent = -1

doc = doctree.Leaf('root')
leaf = doc

for n, line in enumerate(txt) :
	res = rec.search(line)
	if res is None :
		leaf.sub[-1].add_alinea(line)
		continue
	indent = len(res.group('tab'))
	if indent == prev_indent :
		print(n, "1", res.groupdict())
		leaf.grow('li').add_alinea(res.group('line'))
	elif indent == prev_indent + 1 :
		print(n, "2", res.groupdict())
		if res.group('marker') == '*' :
			leaf = leaf.grow('ul')
		elif res.group('marker') == '#' :
			leaf = leaf.grow('ol')
		leaf.grow('li').add_alinea(res.group('line'))
	elif indent == prev_indent - 1 :
		print(n, "3", res.groupdict())
		leaf = leaf.parent
		leaf.grow('li').add_alinea(res.group('line'))

	prev_indent = indent

print(doc)

reference_lst = [
	'alpha',
	'beta',
	[
		'charlie',
		'delta'
	],
	'epsilon'
]