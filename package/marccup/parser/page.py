#!/usr/bin/env python3

""" page parser, a page is a self containing document, with title, sections, and everyting in a single file"""

import re

import oaktree


from marccup.parser.libre import *

class PageParser() :

	def __init__(self, atom_parser=None, debug_dir=None) :

		self.debug_dir = debug_dir

		if atom_parser is None :
			from marccup.parser.atom import AtomParser
			atom_parser = AtomParser(debug_dir)
		self.atom_parser = atom_parser

		from marccup.parser.section import SectionParser
		self.section_parser = SectionParser(atom_parser, debug_dir)

	def parse_page(self, txt) :
		# disabled code
		return
		o_page = oaktree.Leaf('page')

		prev_depth = 0
		prev_node = o_page

		prev_res = None
		stack = list()

		for line in txt.splitlines() :
			title_res = title_rec.match(line)
			if title_res is None :
				# push the line on the stack
				stack.append(line)
			else :
				if prev_res is None : # no title previously found, this must be some introductory text
					o_section = self.parse_section('\n'.join(stack))
					prev_node.attach(o_section)
				else :
					o_section = self.parse_section('\n'.join(stack), prev_res)
					depth = len(prev_res.group('depth'))

					if prev_depth + 1 < depth :
						raise ValueError

					curr_node = prev_node.ancestor_lst[depth-1]
					curr_node.attach(o_section)

					prev_depth = depth
					prev_node = o_section

				prev_res = title_res
				stack = [line,]

		return o_page

	def parse_page(self, txt) :
		raise NotImplementedError
		# disabled code
		return
		o_page = oaktree.Leaf('page', ident=0)

		part_lst = list()
		stack = list()
		for line in txt.splitlines() :
			title_res = title_rec.match(line)
			if title_res is not None :
				block = '\n'.join(stack).strip()
				if block :
					part_lst.append(block)
					stack = list()
				part_lst.append(title_res)
			else :
				stack.append(line)
		block = '\n'.join(stack).strip()
		if block :
			part_lst.append(block)

		print('\n'.join(f'<<<{i}>>>' if isinstance(i, str) else f'\n{i.groupdict()}\n' for i in part_lst))
		print('\n'*3)

		prev_depth = 0
		prev_node = o_page
		prev_title = None
		for part in part_lst :
			print('========')
			print(f'\n\x1b[33m<<<{part}>>>\x1b[0m\n' if isinstance(part, str) else f'\n\x1b[35m{part.groupdict()}\x1b[0m\n')
			print(f"prev_depth: {prev_depth}")
			print(f"prev_node: {prev_node.ancestor_lst} / {prev_node} {prev_node.ident}")
			print(f"prev_title: {prev_title.groupdict() if prev_title is not None else 'null'}")
			if isinstance(part, str) : # text
				print('--- text')
				o_section = self.parse_section(part)
				o_section.nam['depth'] = prev_depth
				prev_node.attach(o_section)
				if prev_title is not None :
					o_section.grow('title').add_text(prev_title.group('title'))
					if prev_title.group('ident') is not None :
						o_section.ident = int(prev_title.group('ident'))
				print(f"\x1b[32mattach\x1b[0m {o_section} to {prev_node} for {o_section.ancestor_lst} with '{part[:25]}...'")
				curr_node = o_section
			else : # title
				print('--- title')
				curr_depth = len(part.group('depth'))
				print(f'curr_depth: {curr_depth}')
				print(f'prev_depth - curr_depth + 1: {prev_depth - curr_depth + 1}')
				if prev_depth + 1 < curr_depth :
					raise ValueError("Bad depth continuity {prev_depth} -> {next_depth}")
				else :
					# increment by one
					prev_node = prev_node.ancestor(prev_depth - curr_depth + 1)
					print(f"new prev_node {prev_node} as {prev_node.ancestor_lst}")
				prev_title = part
				prev_depth = curr_depth

	def parse(self, txt, o_parent=None) :

		txt = self.atom_parser.clean(txt)

		o_page = oaktree.Leaf('page', ident=0, parent=o_parent)

		# split part of text and titles

		part_lst = list()
		stack = list()
		for line in txt.splitlines() :
			title_res = title_rec.match(line)
			if title_res is not None :
				block = '\n'.join(stack).strip()
				if block :
					part_lst.append(block)
					stack = list()
				part_lst.append(title_res)
			else :
				stack.append(line)
		block = '\n'.join(stack).strip()
		if block :
			part_lst.append(block)

		if self.debug_dir is not None :
			from oaktree.proxy.braket import BraketProxy

			debug_lst = list()

			debug_proxy = BraketProxy()
			debug_lst.append('\x1b[37m' + debug_proxy.save(o_page) + '\x1b[0m')

		prev_node = o_page
		prev_depth = 0
		for part in part_lst :
			if isinstance(part, str) : # text
				if self.debug_dir is not None :
					debug_lst.append(f'TEXT :: """{part}"""')
				o_section = self.section_parser._parse_section(part, prev_node)
				# prev_node.sub += o_section.sub

				if self.debug_dir is not None :
					debug_lst.append(f'{o_section} -> {prev_node}')

			else : # title
				if self.debug_dir is not None :
					debug_lst.append(f'TITLE :: \x1b[36m{part}\n{part.groupdict()}\x1b[0m')

				curr_depth = len(part.group('depth'))
				if prev_depth + 1 < curr_depth :
					raise ValueError("Bad depth continuity {prev_depth} -> {next_depth}")
				else :
					if self.debug_dir is not None :
						debug_lst.append(f'\x1b[33m{prev_depth - curr_depth + 1} -> {prev_node} -> {prev_node.ancestor(prev_depth - curr_depth + 1)}\x1b[0m')
					prev_node = prev_node.ancestor(prev_depth - curr_depth + 1)

				o_section = prev_node.grow('section')

				if part.group('ident') is not None :
					o_section.ident = int(part.group('ident'))
				if part.group('depth') is not None :
					o_section.nam['depth'] = len(part.group('depth'))

				o_section.grow('title').add_text(part.group('title'))

				prev_node = o_section
				prev_depth = curr_depth

			if self.debug_dir is not None :
				debug_lst.append('\x1b[37m' + debug_proxy.save(o_page) + '\x1b[0m')

		if self.debug_dir is not None :
			(self.debug_dir / "page.ans").write_text('\n\n'.join(debug_lst))

		return o_page