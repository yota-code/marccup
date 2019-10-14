#!/usr/bin/env python3

import re

import oaktree

from oaktree.xml.common import *

STATE_OUT = 0
STATE_HEADER = 1
STATE_IN = 2
STATE_FOOTER = 3

comment_rec = re.compile(r'<!--.*?-->', re.DOTALL | re.MULTILINE)

def _attach_txt(n_leaf, txt) :
	if txt.strip() != '' :
		n_leaf.attach(txt)

attribute_rec = re.compile(r'\b((?P<space>\w+):)?(?P<key>\w+)="(?P<value>.*?)"', re.DOTALL | re.MULTILINE)
def parse_header(n_leaf, line) :
	n_leaf._tag = line.split()[0]
	for attribute_res in attribute_rec.finditer(line) :
		key = attribute_res.group('key')
		value = attribute_res.group('value')
		if key == 'id' :
			n_leaf.ident = value
		elif key == 'class' :
			n_leaf.style |= set(value.split())
		else :
			n_leaf.nam[key] = value 

def parse_leaf(txt, curs=None, depth=0) :
	if curs is None :
		curs = txt.find(tag_begin)
		
	#print("{0}[{1}...".format('\t'*depth, txt[curs:curs+12]))
	state = 0
	prev = curs
	while curs < len(txt) :
		c = txt[curs]
		#print('\t'*depth, c, state, txt[curs:curs+12])
		curs += 1
		if state == STATE_OUT :
			if c == tag_begin :
				state = STATE_HEADER
				prev = curs
		elif state == STATE_HEADER :
			if c == tag_end :
				state = STATE_IN
				n_leaf = oaktree.Leaf()
				parse_header(n_leaf, txt[prev:curs-1])
				prev = curs	
				if txt[curs-1] == tag_slash :
					state = STATE_FOOTER
		elif state == STATE_IN :
			if c == tag_begin :
				if txt[curs] == tag_slash :
					_attach_txt(n_leaf, txt[prev:curs-1])
					state = STATE_FOOTER
				else :
					n_sub, curs = parse_leaf(txt, curs-1, depth+1)
					n_leaf.attach(n_sub)
					prev = curs
		elif state == STATE_FOOTER :
			if c == tag_end :
				break
	if depth == 0 :
		return n_leaf
	else :
		return n_leaf, curs
		
def load_string(txt) :
	txt = comment_rec.sub('', txt)
	return parse_leaf(txt)
	
if __name__ == '__main__' :
	import oaktree.braket
	txt = """<entry>
	<form>
		<orth>mean</orth>
		<pron>miːn</pron>
	</form>
	<sense n="1">
		<cit type="trans">
			<quote>tenerelpropósito</quote>
		</cit>
	</sense>
	<sense n="2">
		<cit type="trans">
			<quote />
		</cit>
		<cit type="trans">
			<quote>medio</quote>
		</cit>
	</sense>
	<sense n="3">
		<cit type="trans">
			<quote>significar</quote>
		</cit>
	</sense>
	<sense n="4">
		<cit type="trans">
			<quote>quererdecir</quote>
		</cit>
	</sense>
</entry>"""
	doc = load_string(txt)
	print(oaktree.braket.dump(doc))
	print(doc.only_text('|'))
	
