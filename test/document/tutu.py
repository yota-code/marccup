#!/usr/bin/env python3

from pathlib import Path

u = 1000
for txt in [i.strip() for i in Path("__doc__.tsv").read_text().split('\n\n')] :
	header, null, content = txt.partition('.')
	Path(f"{u:05d}.txt").write_text(f'= {header}\n\n{content}')
	u += 1
