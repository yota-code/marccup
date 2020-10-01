#!/usr/bin/env python3

import os

import cherrypy

from cc_pathlib import Path

import oaktree
import oaktree.proxy.html5
import oaktree.proxy.braket

import marccup.parser.section
import marccup.composer.html5


class MarccupProxy() :

	def __init__(self) :
		self.repo_dir = Path( os.environ['MARCCUP_repo_DIR'] ).resolve()

	def _get_file(self, book_key, local_pth) :
		try :
			pth = (self.repo_dir / book_key / local_pth).or_archive
			if pth.suffix == '.br' :
				cherrypy.response.headers['Content-Encoding'] = 'br'
			return pth.read_bytes()
		except FileNotFoundError :
			raise cherrypy.HTTPError(404)

	def _get_json(self, book_key, name) :
		return self._get_file(book_key, f".cache/{name}.json")

	@cherrypy.expose
	def _get_section(self, book_key, ident) :
		print(f"MarccupProxy.section({book_key}, {ident})")

		local_pth = f".cache/part/{ident:04d}"
		cache_pth = (self.repo_dir / book_key / local_pth)

		if not cache_pth.or_archive.is_file() :
			self._prep_section(book_key, ident)

		return self._get_file(book_key, local_pth)

	def _prep_section(self, book_key, ident) :

		base_dir = self.repo_dir / book_key

		b = marccup.parser.generic.GenericParser()
		u = marccup.composer.html5.Html5Composer()

		t = (base_dir / 'part' / f'{ident:04d}').read_text()

		o = b.parse(t)

		g = oaktree.proxy.braket.BraketProxy()
		k = oaktree.proxy.braket.BraketProxy(indent='')

		g.save(o, Path( base_dir / ".tmp" / f'{ident:04d}.parsed.bkt'))
		#k.save(o, Path( base_dir / ".tmp" / f'{ident:04d}.parsednoindent.bkt'))

		h = oaktree.Leaf('tmp')
		u.compose(o, h)

		#g.save(h.sub[0], Path( base_dir / ".tmp" / f'{ident:04d}.composed.bkt'))
		#k.save(h.sub[0], Path( base_dir / ".tmp" / f'{ident:04d}.composednoindent.bkt'))

		f = oaktree.proxy.html5.Html5Proxy(indent='', fragment=True)
		#f.save(h.sub[0], Path( base_dir / ".tmp" / f'{ident:04d}.result.html'))
		f.save(h.sub[0], Path( base_dir / ".cache" / "part" / f'{ident:04d}'))

		return f.save(h.sub[0])