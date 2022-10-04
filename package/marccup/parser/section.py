#!/usr/bin/env python3

import oaktree

# from marccup.parser.generic import GenericParser
from marccup.parser.libre import *

# class SectionParser(GenericParser) :
# 	""" a section is a part composed of one or more paragraph and a single optionnal title """

# 	def parse_section(self, txt) :

# 		txt = self.expand_shortcut(txt)

# 		o_section = self._parse_section(txt)

# 		return o_section


class SectionParser() :
	"""
	a section is someting
	"""
	def __init__(self, atom_parser=None, debug_dir=None) :

		self.debug_dir = debug_dir

		if atom_parser is None :
			from marccup.parser.atom import AtomParser
			atom_parser = AtomParser(debug_dir)
		self.atom_parser = atom_parser

	# def clean(self, txt) :
	# 	# right trim each line
	# 	lst = [ line.rstrip() for line in txt.splitlines() ]

	# 	# remove empty lines at start or at the end of the section
	# 	while lst and not lst[0].strip() :
	# 		lst.pop(0)
	# 	while lst and not lst[-1].strip() :
	# 		lst.pop(-1)
	# 	txt = '\n'.join(lst)

	# 	# format paragragraphs properly
	# 	txt = paragraph_sep_rec.sub('\n\n', txt)

	# 	return txt

	def parse(self, txt, o_parent=None) :
		if self.debug_dir is not None :
			debug_lst = list()
			debug_lst.append(f'ORIGINAL :: """{txt}"""\n\n----\n')
		
		txt = self.atom_parser.clean(txt)

		if self.debug_dir is not None :
			debug_lst.append(f'CLEANED :: """{txt}"""\n\n----\n')
			for k, v in self.atom_parser.atom_map.items() :
				debug_lst.append(f"{k} :: {v}")
			(self.debug_dir / 'clean.txt').write_text( '\n'.join(debug_lst) )

		# if '\n\n' in txt :
		o_section = self._parse_section(txt, o_parent)
		# elif '\n' in txt :
		# 	self._parse_paragraph(o_parent, txt)
		# else :
		# 	self._parse_alinea(o_parent, txt)

		return o_section

	def _parse_section(self, txt, o_parent=None) :
		""" a section is a part of text which contains many paragraphs but no title """

		o_section = oaktree.Leaf('section', parent=o_parent)
		# o_section.ident = id(o_section) & 0xFFFF

		for paragraph_txt in txt.split('\n\n') :
			print(f">>>\n{paragraph_txt}\n<<<")
			o_paragraph = self._parse_paragraph(paragraph_txt, o_section)

		return o_section

	def _parse_paragraph(self, txt, o_parent=None) :
		# if self.debug_dir is not None :
		# 	print(f'SectionParser._parse_paragraph({txt[:32]}..., {o_parent.tag})')

		if ( res := atom_block_packed_rec.match(txt) ) is not None :
			o_atom = self.atom_parser.parse(res.groupdict(), o_parent, True)
			return o_atom
		else :
			for alinea_txt in txt.splitlines() :
				# let's check that is is a not a bulleted or numbered list
				if not bullet_list_rec.match(alinea_txt) :
					break # there is one normal alinea inside, abort !
			else :
				# only bullets ! let's parse it somewhere else
				return self._parse_list(txt, o_parent)

			alinea_lst = txt.splitlines()

			o_paragraph = oaktree.Leaf('paragraph', parent=o_parent)

			# if the last line is a paragraph ident, parse it, and pop it
			if ( res := paragraph_ident_rec.match(alinea_lst[-1]) ) is not None :
				o_paragraph.ident = int(res.group('ident'))
				alinea_lst.pop(-1)

			for alinea_txt in alinea_lst :
				self._parse_alinea(alinea_txt, o_paragraph)

			return o_paragraph

	def _parse_alinea(self, txt, o_parent=None) :
		"""
		txt: should not contain any line feed
		tag: can be something else than 'alinea'. most of the time it will be 'li'
		"""

		if '\n' in txt : 
			raise ValueError()

		o_alinea = oaktree.Leaf('alinea', parent=o_parent)

		res = alinea_ident_rec.search(txt)
		if res is not None :
			# if the alinea ident exists, parse it and cut it
			o_alinea.ident = int(res.group('ident'))
			txt = txt[:res.start()]

		txt = txt.rstrip()

		# the first level atoms have already been parsed
		prev = None
		for res in atom_line_packed_rec.finditer(txt) :
			curr = res.start()
			s = txt[prev:curr]
			if s.strip() :
				o_alinea.add_text(s)
			o_atom = self.atom_parser.parse(res.groupdict(), o_alinea, False)
			prev = res.end()
		s = txt[prev:None]
		if s.strip() :
			o_alinea.add_text(s)

		return o_alinea

	def _parse_list(self, txt, o_parent=None) :

		prev_indent = -1

		o_item = o_parent
		for n, line in enumerate(txt.splitlines()) :

			res = bullet_list_rec.search(line)
			curr_indent = len(res.group('tabs'))

			to_grow = False
			
			if curr_indent == prev_indent :
				# same level, nothing to add, o_list should exists
				pass
			elif curr_indent == prev_indent + 1 :
				# increased indentation level by 1, will create a new ol/ul group
				if res.group('marker') == '*' :
					o_list = o_item.grow('ul')
				elif res.group('marker') == '#' :
					o_list = o_item.grow('ol')
				else :
					raise ValueError(f"unknown marker: {line}")
			elif curr_indent < prev_indent :
				# reduced indentation level
				o_list = o_list.parent_n(2 * (prev_indent - curr_indent))
			else :
				raise ValueError(f"erroneous indentation:\n{txt}")

			o_item = self._parse_alinea(res.group('line'), o_item)
			o_item.tag = 'li'

			prev_indent = curr_indent
