#!/usr/bin/env python3

import json

import oaktree

class Line(oaktree.Line) :
	
	def compose_object(self) :
		return [
			[
				self.space, self.tag, str(self.ident)
			],
			[
				[str(i) for i in self.pos],
				{str(k) : str(v) for v, k in self.nam.items()},
				list(self.flag),
				list(self.style)
			]
		]


