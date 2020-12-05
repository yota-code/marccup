#!/usr/bin/env python3

import collections
import datetime
import os

import cherrypy

from cc_pathlib import Path

import oaktree
import oaktree.proxy.html5
import oaktree.proxy.braket

import marccup.parser.book
import marccup.composer.html5

def todo(dst, * src_lst) :
	if not dst.is_file() :
		return True

	dst_time = dst.stat().st_mtime
	for src in src_lst :
		if src.stat().st_mtime >= dst_time :
			return True
	
	return False

class MarccupShelf() :
	""" un objet générique, à instancier une seule fois, qui maintient la liste de tous les livres disponibles, permet la mise à jour des caches et la generation à la volée """
	def __init__(self) :
		self.repo_dir = Path( os.environ['MARCCUP_repo_DIR'] )

		self.book_set = set()

		for book_key in self.scan(self.repo_dir) :
			self.install(book_key)
			self.book_set.add(book_key)

		print(self.book_set)

	def is_valid(self, book_key) :
		return ( (self.repo_dir / book_key / 'index').is_file() and (self.repo_dir / book_key / 'part').is_dir() )

	def scan(self, root_dir) :
		for pth in root_dir.iterdir() :
			if ( (pth / 'index').is_file() and (pth / 'part').is_dir() ) :
				yield str(pth.relative_to(self.repo_dir))
			else :
				if pth.is_dir() and pth.name != 'part' :
					yield from self.scan(pth)
			
	def install(self, book_key) :

		if not self.is_valid(book_key) :
			raise ValueError

		cache_dir = self.repo_dir / book_key / '.cache' / 'part'
		cache_dir.make_dirs()

		self._prep_index(book_key)
		self._prep_refer(book_key)

	def _prep_index(self, book_key) :

		src_pth = self.repo_dir / book_key / 'index'

		txt = src_pth.read_text()

		u = marccup.parser.book.BookParser()
		index_lst = u.parse_index(txt)

		dst_pth = self.repo_dir / book_key / '.cache' / 'index.json'
		dst_pth.save(index_lst)

		return index_lst

	def _prep_refer(self, book_key) :

		# un fichier appelé référence, qui contient, pour chaque section, la liste des
		# alinea, paragraphes, figures, equations (ou l'inverse)
		# ce fichier est créé s'il n'existe pas, mais il n'est mis à jour que lorsqu'un fichier est modifié
		# ou lors d'une requête explicite

		refer_map = dict()

		section_set = set(
			int( pth.name ) for pth in (self.repo_dir / book_key / 'part').glob('*')
		)

		other_set = set()
		for s_ident in sorted(section_set) :

			pth = self.repo_dir / book_key / 'part' / f'{s_ident:04d}'

			txt = pth.read_text()

			u = marccup.parser.book.BookParser()
			o_section = u.parse(txt)

			b = oaktree.proxy.braket.BraketProxy()
			b.save(o_section, Path('debug.bkt'))

			for o in o_section.walk() :
				if o.ident != None :
					other_set.add(o.ident)
					if o.tag not in refer_map :
						refer_map[o.tag] = collections.defaultdict(set)
					refer_map[o.tag][s_ident].add(o.ident)
			
		refer_map['__next__'] = max(section_set | other_set) + 1

		dst_pth = self.repo_dir / book_key / '.cache' / 'refer.json'
		dst_pth.save(refer_map)

		print(refer_map)

		return refer_map

	def __getitem__(self, key) :
		if key not in self.book_set :
			self.install(key)
		return self.book_map[key]

if __name__ == '__main__' :
	p = BookShelf()