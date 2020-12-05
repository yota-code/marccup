#!/usr/bin/env python3

class Atom() :
	def __init__(self, res, content) :
		self.space = res.group('space')
		self.tag = res.group('tag')

		self.is_block = len(res.group('marker')) == 3

		self.content = content.split('|')

	def __str__(self) :
		space = '' if self.space is None else f'{self.space}.'
		m = 3 if self.is_block else 1
		return f"\\{space}{self.tag}{'<'*m}{'|'.join(self.content)}{'>'*m}"
