#!/usr/bin/env python3

import pathlib

import oaktree
import oaktree.braket

from oaktree.braket.common import *

from oaktree.auto_rw import auto_write


"""
the main tree is stored in file_dir/__root__.bkt

"""

_esc_leaf = [('&', '&esc;'), ('|', '&pipe;'), ('>', '&cbkt;'), ('<', '&obkt;')]

def _dump_file(n_leaf, root_dir) :
	ident, tag = n_leaf.ident, n_leaf.tag # backup
	n_leaf.ident, n_leaf.tag = None, '__file__' # hack
	file_pth = (root_dir / tag / str(ident))
	if not file_pth.parent.is_dir() :
		file_pth.parent.mkdir()
	oaktree.braket.dump(n_leaf, file_pth)
	n_leaf.ident, n_leaf.tag = ident, tag # restore


class Leaf(oaktree.braket.Leaf, oaktree.braket.Line) :

	@auto_write
	def compose(self, root_dir, tag_set, _depth=0, _aw=None) :
		if self._indent_mode is None :
			self._re_indent()
		
		before_header, after_header, before_footer, after_footer = indentation(self._indent_mode, _depth)
		
		_aw(before_header)
		_aw(markup_begin)
		if isinstance(self, ExternalLeaf) or (self.tag in tag_set and self.ident is not None) :
			_aw("@")
			Leaf._compose_space(self, _aw=_aw)
			_aw(self.tag)
			Leaf._compose_ident(self, _aw=_aw)
			_dump_file(self, root_dir)
		else :
			Leaf._compose_header(self, _aw=_aw)
			if self.sub :
				_aw(markup_separator)
				_aw(after_header)
				previous_was_str = False
				for k in self.sub :
					if isinstance(k, oaktree.Leaf) :
						if previous_was_str :
							_aw('\n')
						Leaf.compose(k, root_dir, tag_set, _depth+1, _aw=_aw)
						previous_was_str = False
					else :
						if previous_was_str :
							_aw(markup_separator)
							if self._indent_mode < oaktree.CONTAINER :
								_aw('\n')
						_aw(protect(k, _esc_leaf))
						previous_was_str = True
				_aw(before_footer)
				_aw(markup_separator)
				Leaf._compose_footer(self, _aw=_aw)
		_aw(markup_end)
		_aw(after_footer)
		
	def parse(self, s, n=0, depth=0) :
		#print(">>>\t{0}{1:08X} {2!r}".format('>>>\t'*depth, id(self), s[n:n+32]))
		status = 0
		brace = 0
		prev_n = n
		while n < len(s) :
			c = s[n]
			#print("{0} {1:4d}'{2!r}' {3}".format('\t-'*depth, n, c, status))
			n += 1
			if c == '{' :
				brace += 1
			elif c == '}' :
				brace -= 1
			if status == 0 : # before the header
				if c == '<' : # begining of the header
					status = 1
					prev_n = n
					brace = 0
			elif status == 1 : # inside the header
				if brace == 0 and c == '|' : # end of the header
					self._parse_header(s[prev_n:n-1])
					prev_n = n
					brace = 0
					status = 2
				elif c == '>' :
					if brace != 0 :
						raise SyntaxError("non matching braket before: ...{0}".format(s[n-15:n]))
					self._parse_header(s[prev_n:n-1])
					break
			elif status == 2 : # parsing content
				if c == '<' :
					self.add_text(restore(s[prev_n:n-1], _esc_leaf).strip())
					if s[n] == '@' :
						prev_n = n
						n = s.index('>', prev_n) + 1
						tag, ident = s[prev_n+1:n-1].split('#')
						n_sub = Leaf(tag, ident)
						n_sub._loaded = False
					else :
						n_sub, n = Leaf().parse(s, n-1, depth+1)
					self.attach(n_sub)
					prev_n = n
				elif c == '|' and brace == 0 :
					self.add_text(restore(s[prev_n:n-1], _esc_leaf).strip())
					prev_n = n
				elif c == '>' :
					if brace != 0 :
						raise SyntaxError("non matching braces before: ...{0}".format(s[n-15:n]))
					prev_n = n
					break
		if status <= 0 :
			return None, n
		if depth == 0 :
			self._post_parsing()
		return self, n


def _clear_dir(pth) :
	for sub in pth.iterdir() :
		if sub.is_dir() :
			_clear_dir(sub)
			sub.rmdir()
		else :
			sub.unlink()
		
class ExternalLeaf(Leaf) :
	pass
	
def partial_load(pth) :
	""" load only the root file """
	root_pth = pth / "__root__.bkt"	
	if isinstance(pth, pathlib.Path) :
		with root_pth.open('rt', encoding='utf8') as fid :
			n_leaf, null = Leaf().parse(fid.read())
	n_leaf._root_pth = root_pth
	return n_leaf
	
def full_load(n_leaf) :
	root_pth = n_leaf.root._root_pth
	for n_sub in n_leaf.walk_breadth() :
		if not n_sub._loaded :
			space = n_sub.space
			tag = n_sub.tag
			ident = n_sub.ident
			filename = (root_pth.parent / tag / ident)
			n_new = n_sub.replace(oaktree.braket.load(filename))
			n_new.space = space
			n_new.tag = tag
			n_new.ident = ident
			

def dump(self, pth, * tag_lst) :
	if isinstance(pth, str) :
		pth = pathlib.Path(pth)
		
	tag_set = set(tag_lst)

	if pth.is_dir() :
		raise ValueError("Can not override existing directory:{0}".format(pth))
	else :
		pth.mkdir()
		
	root_pth = pth / "__root__.bkt"
	
	Leaf.compose(self, pth, tag_set, _aw=root_pth)

