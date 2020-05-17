#!/usr/bin/env python3

import re

title_rec = re.compile(r'^\s*(?P<depth>=+)\s*(?P<title>.*?)(\s*§(?P<ident>\d+))?$')


paragraph_ident_rec = re.compile(r'^#(?P<ident>[0-9]+)$')

alinea_ident_rec = re.compile(r'§(?P<ident>[0-9]+)$')
paragraph_ident_rec = re.compile(r'^§(?P<ident>[0-9]+)$')

line_rec = re.compile(r'\\((?P<space>[a-z]+)\.)?(?P<tag>[a-z_]+)(?P<marker><)')
block_rec = re.compile(r'\\((?P<space>[a-z]+)\.)?(?P<tag>[a-z_]+)(?P<marker><<<)')

marker_open_rec = re.compile(r'\\((?P<space>[a-z]+)\.)?(?P<tag>[a-z]+)<(<<)?')
marker_close_rec = re.compile(r'>(>>)?')

atom_line_rec = re.compile(r'\x02ATOM\[(?P<atom_n>\d+)\]\x03')
atom_block_rec = re.compile(r'^\x02ATOM\[(?P<atom_n>\d+)\]\x03(\s*§(?P<ident>[0-9]+))?$')

paragraph_sep_rec = re.compile(r'\n\n+', re.MULTILINE)


bullet_list_rec = re.compile(r'^(?P<tabs>\t*)(?P<marker>[\*\#])\s+(?P<line>.*)$')

table_split_rec = re.compile('^\s*---\s*$', re.MULTILINE)
table_span_rec = re.compile(r'^(r(?P<row_n>[0-9]+))?(c(?P<col_n>[0-9]+))?!')
