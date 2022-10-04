#!/usr/bin/env python3

from pathlib import Path

import oaktree

import oaktree.proxy.html5

from marccup.parser.section import SectionParser
from marccup.parser.page import PageParser

from marccup.composer.html5 import Html5Composer

import marccup.parser.libre as libre

def parse_section(txt) :
	return SectionParser().parse(txt)

def parse_file(pth) :
	if pth.is_dir() and pth / '__doc__.mcp' :
		txt = (pth / '__doc__.mcp').read_text()
		return PageParser().parse_page(txt)
	
	if pth.is_file() :
		txt = pth.read_text()

def parse_text(txt) :
	title_lst = list( libre.title_rec.finditer(txt) )

	if len(title_lst) == 0 or ( len(title_lst) == 0 and txt.lstrip().startswith('= ') ) :
		return SectionParser().parse_section(txt)

	if len(title_lst) > 1 :
		return PageParser().parse_page(txt)

def compose_html(obj, tag=None) :
	h = oaktree.Leaf('tmp' if tag is None else tag)
	Html5Composer().compose(obj, h)

	f = oaktree.proxy.html5.Html5Proxy(indent='\t', fragment=True)
	return f.save(h.sub[0] if tag is None else h)

