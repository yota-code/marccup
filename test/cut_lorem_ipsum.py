#!/usr/bin/env python3

import sys

from cc_pathlib import Path

import random

random.seed(1234)

u = 1000
r = list()
l = 1
for txt in [i.strip() for i in Path(sys.argv[1]).read_text().split('\n\n')] :
	header, null, content = txt.partition('.')
	content = '\n'.join(line.strip() for line in content.replace('. ', '.\n').split('\n'))
	Path(f"{u:04d}.bkt").write_text(f'= {header}\n\n{content}')
	r.append([l, f"{u:04d}"])
	u += 1
	p = int(random.random() * 6.0 + 0.66) + 1
	if p > l :
		l += 1
	elif p < l :
		l = p
	l = min(4, l)
	l = max(1, l)

Path("__doc__.tsv").save(r)
