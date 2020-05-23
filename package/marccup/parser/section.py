#!/usr/bin/env python3

from marccup.parser.generic import GenericParser
from marccup.parser.libre import *


class SectionParser(GenericParser) :
	""" a section is a part composed of one or more paragraph (and no title ?) """

	def parse_section(self, txt) :

		txt = self.expand_shortcut(txt)

		o_section = self._parse_section(txt)

		return o_section

