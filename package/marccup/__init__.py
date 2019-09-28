#!/usr/bin/env python3

import bracket

from cc_pathlib import Path

class Interpreter() :

	def __init__(self) :
		pass

	def load_document(self, root_dir) :
		toc = [
			[int(a), int(b), * c]
			for a, b, * c in (root_dir / "__doc__.tsv").load()
		]
		print(toc)


if __name__ == "__main__" :
	u = Interpreter()
	u.load_document(Path('.'))