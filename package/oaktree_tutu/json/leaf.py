#!/usr/bin/env python3

import io
import json

import oaktree

from oaktree.json.line import Line

from oaktree.auto_rw import auto_write

class Leaf(oaktree.Leaf, Line) :
	
	@auto_write
	def compose(self, _aw=None, compact=False) :
		if compact :
			p = {'indent': None, 'separators': (',', ':')}
		else :
			p = {'indent': '\t'}
		_aw(json.dumps(
			Leaf._build_json(self), ensure_ascii=False, sort_keys=True, ** p
		))
					
	def _build_json(self) :
		m = dict()
		m['tag'] = self.tag
		for attr, collapse in leaf_attr_collapse :
			p = getattr(self, attr)
			if p :
				m[attr] = collapse(p)
		return m

def set_to_list(s) :
	return list(sorted(s))
	
def sub_to_list(s) :
	return [
		Leaf._build_json(sub) if isinstance(sub, oaktree.Leaf) else str(sub)
		for sub in s
	]
	
leaf_attr_collapse = [
	['space', str],
	['ident', str],
	['pos', list],
	['nam', dict],
	['flag', set_to_list],
	['style', set_to_list],
	['sub', sub_to_list]
]

