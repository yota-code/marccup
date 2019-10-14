#!/usr/bin/env python3

import os, fnmatch
import pathlib

""" a "folder" is meant to be used on data structures composed of many "files" stored at
level zero. All files are sister leaves (same tag), with a unique ident.

Pour un noeud de haut niveau, ne contenant que des éléments du meme type, ayant tous un identifiant
le tout est stocké dans un répertoire,
qui contient lui meme 16 dossier de 0 à F
qui contiennent des fichiers, nommé suivant l'identifiant,
qui contiennent chacun un noeud de second niveau

chargement lazy
---------------
Les fichiers sont tous listés comme sous-noeud du noeud principal
Leur accès est possible par dictionnaire
à l'enregistrement,
	seuls les entrées qui ont été chargées sont ré-écrites
	les entrées 

"""

import oaktree.braket

class FolderLeaf(oaktree.Leaf) :
	
	def get_or_create(self, ident=None) :
		try :
			return self.pick_ident(ident)
		else :
			if ident is None :
				ident = max(self.folder) + 1 if len(self.sub) else 0
			n_leaf = self.grow(self._default_sub_tag, ident)
			self.folder[ident] = n_leaf
			return n_leaf

rec_header = re.compile('\s*<(.*?)\|', re.UNICODE | re.MULTILINE | re.DOTALL)

class LazyLeaf(oaktree.braket.Leaf) :
	
	_read_only = False
	
	@property
	def read_only(self) :
		self._read_only = True
		return self
	
	@property
	def pth(self) :
		return pathlib.Path('{0}.bkt'.format(self.parent.tag)) / '{0:08X}.bkt'.format(self.ident)
	
	def __enter__(self) :
		if self.pth.is_file() :
			print("load...", self.pth)
			with self.pth.open('rt', encoding='utf8') as f :
				txt  = f.read()
			n_leaf = oaktree.braket.load(txt)
			n_leaf.ident = self.ident
		else :
			if self._read_only :
				raise FileNotFoundError("no such ident:{0}".format(self.ident))
			print("create...", self.pth)
			txt = ""
			n_leaf = oaktree.braket.Leaf(self.tag, self.ident)
		if not self._read_only :
			self._content_cache = txt
		self._leaf_cache = n_leaf
		return self.replace(n_leaf)
		
	def __exit__(self, exc_type, exc_value, traceback) :
		if self._read_only :
			self._read_only = False
		else :
			ident = self._leaf_cache.ident
			self._leaf_cache.ident = None
			_content_result = oaktree.braket.dump(self._leaf_cache)
			self._leaf_cache.ident = ident
			if _content_result != self._content_cache :
				print("save...", self.pth)
				with self.pth.open('wt', encoding='utf8') as f :
					f.write(_content_result)
		self._leaf_cache.replace(self)

	def parse(self, txt) :
		s = rec_header.match(txt).group(1)
		oaktree.braket.Leaf._parse_header(self, s)
		return self
		
def dump(n_folder, _output=pathlib.Path('.')) :
	"""
	_out: a directory Path()
	
	each leaf of the folder will be saved as _out / folder.tag / (n_item.ident + bkt)
	"""
	
	new_set = set(i.ident for i in n_folder.iterleaf)
	_output /= (n_folder.tag + '.bkt')
	if _output.exists() :
		if _output.is_dir() :
			old_set = set(int(i.stem, 16) for i in _output.glob('*.bkt'))
		else :
			raise ValueError("not a valid directory:{0}".format(_output))
	else :
		old_set = set()
		_output.mkdir()
	
	for n_sub in n_folder.iterleaf :
		if isinstance(n_sub, LazyLeaf) :
			continue
		ident = n_sub.ident
		pth = _output / "{0:04X}".format(ident)
		print("write leaf to <{0}>".format(pth))
		n_sub.ident = None
		oaktree.braket.dump(n_sub, pth)
		n_sub.ident = ident
		
	print("garbage:", ", ".join(str(i) for i in (old_set - new_set)))
		
def load(_dir) :
	if not _dir.is_dir() :
		raise ValueError("must be a valid directory:{0}".format(_dir))
	n_folder = FolderLeaf(_dir.stem)
	for pth in _dir.glob('*') :
		try :
			ident = int(pth.stem, 16)
		except :
			Warning("Skipped file:{0}".format(pth))
		n_file = LazyLeaf()
		with pth.open('rt', encoding='utf8') as fid :
			n_file.parse(fid.read())
		n_file.ident = ident
		n_folder.attach(n_file)
		n_folder._default_sub_tag = n_file.tag
	return n_folder
	
