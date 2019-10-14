#!/usr/bin/env python3

import os, fnmatch
import pathlib
import re, collections

from pathlib import Path as P

import logging as log

log.basicConfig(level=log.CRITICAL)

"""
FolderLeaf and FileLeaf are meant to be used on data structures composed of many similar
"files" stored at level zero, in a unique folder.

All files are all sister leaves (same tag, which will also be the name of the folder), with a
unique ident which must be a simple file name (no more constraint on integer stuff) matching :
'^[0-9A-F]+$'

files are saved as ./tag.bkt/ident

ident will be incrementally attributed


chargement lazy
---------------
Les fichiers sont tous listés comme sous-noeud d'un noeud __file__
(Leur accès est possible par dictionnaire)
à l'enregistrement,
	seuls les entrées qui ont été chargées sont ré-écrites
	les entrées 

"""

import oaktree.braket

ident_rec = re.compile('^[0-9A-F]+$')
	
class FolderLeaf(oaktree.Leaf) :
	
	def down(self, ident) :
		for n_sub in self :
			if n_sub.ident == ident :
				return n_sub
		raise KeyError("no ident={0}{1} in {2}".format(type(ident), ident,
			", ".join("{0}{1}".format(type(n.ident), repr(n.ident)) for n in self)))
	
	def __init__(self, file_dir) :
		
		log.info('FolderLeaf({0})'.format(file_dir))
		
		self._folder_dir = file_dir.parent
		self._file_tag = file_dir.stem
		
		oaktree.Leaf.__init__(self)
		
		if not self.pth().is_dir() :
			self.pth().mkdir()
		else :
			self.load()
		
	def _refresh_folder(self) :
		self.folder = {
			n_sub.ident : n_sub
			for n_sub in self
		}
		return self.folder
		
	def load(self) :
		""" lazy load all files found in the folder """
		self.sub = list()		
		for pth in (self._folder_dir / '{0}.bkt'.format(self._file_tag)).glob('*') :
			fnm = pth.stem
			if ident_rec.match(pth.stem) :
				self.grow(self._file_tag, pth.stem, cls=FileLeaf).load()
			else :
				log.warning("{0}:file will not be loaded".format(pth))
		self._refresh_folder()
		return self
		
	def dump(self) :
		""" write down all files which are fully loaded """
		new_set = set(n_sub.ident for n_sub in self.iterleaf)
		if self.pth().exists() :
			if self.pth().is_dir() and str(self.pth()).endswith('.bkt') :
				# we are most probably updating an existing FolderLeaf
				old_set = set()
				for file_pth in self.pth().glob('*') :
					if file_pth.is_file() :
						try :
							old_set.add(file_pth.stem)
						except :
							log.warning("Invalid file:{0}".format(file_pth))
			else :
				raise ValueError("Not a valid directory:{0}".format(file_dir))
		else :
			self.pth().mkdir()
		
		for n_sub in self :
			if not isinstance(n_sub, FileLeaf) or n_sub._full_load :
				n_sub.fclose()
				
		trash_set = old_set - new_set
		
		for ident in trash_set :
			file_pth = self.pth(n_sub.ident)
			file_pth.unlink()
		
	def pth(self, ident=None) :
		if ident is None :
			return self._folder_dir / '{0}.bkt'.format(self._file_tag)
		else :
			return self._folder_dir / '{0}.bkt'.format(self._file_tag) / ident
	
	def get_or_create(self, ident) :
		""" return a new lazy FileLeaf """
		if isintance(ident, int) :
			ident = "{0:04X}".format(ident)
		if ident not in self.folder :
			self.folder[ident] = self.grow(self._file_tag, ident, cls=FileLeaf)
		return self.folder[ident]
		
	def insert_or_update(self, leaf) :
		
		if isinstance(leaf, str) :
			# n_file is a string in the oaktree.braket format
			n_file, n = FileLeaf().parse(leaf)
		else :
			raise ValueError("Not implemented yet ...")
		
		# test properties
		if n_file.tag != self._file_tag	:
			raise ValueError("Wrong tag: {0}".format(n_file.tag))
		if not ident_rec.match(n_file.ident) :
			raise ValueError("Wrong ident: {0}".format(n_file.ident))
			
		if n_file.ident in self.folder :
			self.folder[n_file.ident].replace(n_file)
		else :
			self.attach(n_file)
			self.folder[n_file.tag] = n_file
		
		return n_file

rec_file_header = re.compile('^\s*<__file__\s?(?P<line>.*?)[\|\>]', re.UNICODE | re.MULTILINE | re.DOTALL)

class FileLeaf(oaktree.braket.Leaf) :
	
	_read_only = False
	_full_load = True # True by default, so can __enter__(), and it will be False when __exit__()
	
	_indent_mode = oaktree.TREE
	
	def load(self) :
		""" must be and existing FileLeaf and an existing file """
		pth = self.parent.pth(self.ident)
		log.debug("FileLeaf.load():{0}".format(pth))
		with pth.open('rt', encoding='utf8') as fid :
			line = fid.readline()
			line = rec_file_header.match(line).group('line')
		oaktree.braket.Line.parse(self, line)
		self._full_load = False
		return self
		
	def pth(self) :
		return self.parent.pth(self.ident)
		
	def fopen(self) :
		""" take a lazy loaded leaf, load it fully, replace and return """
		if self._full_load :
			log.warning("Already fully loaded {0}#{1}".format(self.tag, self.ident))
			return self
			
		if self.pth().is_file() :
			n_full = oaktree.braket.load(self.pth())
			n_full.__class__ = FileLeaf
			n_full.ident = self.ident
			n_full.tag = self.tag
		else :
			if self._read_only :
				raise FileNotFoundError("No such file:{0}".format(self.ident))
			n_full = FileLeaf(self.tag, self.ident)
			
		n_full._full_load = True
		self.replace(n_full)
		self.parent.folder[self.ident] = n_full
		return n_full
		
	def fclose(self) :
		""" take a fully loaded leaf, dump it, keeps lazy, replace and return """
		
		if not (self._full_load) and self.pth().exists() :
			log.warning("Not fully loaded")
			return self
					
		n_full = self # retrieve leaf
		pth = self.pth()
		
		n_lazy = FileLeaf(n_full.tag, n_full.ident, pos=n_full.pos, nam=n_full.nam, flag=n_full.flag, style=n_full.style)
		
		_dump_file(n_full, pth)
		
		n_lazy._full_load = False
		n_full.replace(n_lazy)
		self.parent.folder[self.ident] = n_lazy
		
		return n_lazy
			
	def __enter__(self) :
		return self.fopen()
			
	def __exit__(self, exc_type, exc_value, traceback) :
		self.fclose()
		
	@property
	def read_only(self) :
		self._read_only = True
		return self
		
def _dump_file(n_leaf, pth) :
	ident, tag = n_leaf.ident, n_leaf.tag # backup
	n_leaf.ident, n_leaf.tag = None, '__file__' # hack-it
	oaktree.braket.dump(n_leaf, pth)
	n_leaf.ident, n_leaf.tag = ident, tag # restore
	
def dump(n_leaf, output=None) :
	""" output is the parent dir name, mainly as a conversion from other formats """
	tag = check_folder(n_leaf)
	if isinstance(output, P) :
		if output.stem != tag :
			raise ValueError("unexpected tag name {0} vs {1}".format(output.stem, tag))
		n_folder = oaktree.filder.FolderLeaf(output)
		for n_sub in n_leaf :
			_dump_file(n_sub, n_folder.pth(ident))
			
def load(pth) :
	return FolderLeaf(pth)
	
def _load_file(pth, parent) :
	# unused
	with pth.open('rt', encoding='utf8') as fid :
		n_file = FileLeaf.parse(fid.read)

def check_folder(n_leaf) :
	""" check if a given (a priori generic) oaktree is also a valid folder """
	prev_tag = None
	ident_set = set()
	for n_sub in n_leaf :
		if ident_rec.match(n_sub.ident) :
			if ident in ident_set :
				raise ValueError("all idents must be unique")
			if prev_tag is not None and n_sub.tag != prev_tag :
				raise ValueError("all tag must be identical")
			ident_set.add(ident)
			prev_tag = n_sub.tag
		else :
			raise ValueError("{0}:ident must be {1}".format(n_sub.ident, ident_rec.pattern))
	return prev_tag
