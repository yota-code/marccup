#!/usr/bin/env python3

import datetime
import os

import cherrypy

from cc_pathlib import Path

import oaktree
import oaktree.proxy.html5
import oaktree.proxy.braket

import marccup.parser.book
import marccup.composer.html5
import marccup.server.shelf
import marccup.server.proxy
# import marccup.parser.generic

# u.parse_index("/mnt/workbench/source/marccup/test/book/exemple-01")

class MarccupServer() :

	def __init__(self) :
		self.static_dir = Path(os.environ['MARCCUP_static_DIR'])

		self.shelf = marccup.server.shelf.MarccupShelf()
		self.proxy = marccup.server.proxy.MarccupProxy()

		self.to_html5 = marccup.composer.html5.Html5Composer()
		
	@cherrypy.expose
	def index(self, * pos, ** nam) :
		return (self.static_dir / "html" / "index.html").read_bytes()

	@cherrypy.expose
	def reader(self, * pos, ** nam) :
		print(f"MarccupServer.reader({pos}, {nam})")
		return (self.static_dir / "html" / "reader.html").read_bytes()

	@cherrypy.expose
	def monaco(self, * pos, ** nam) :
		print(f"MarccupServer.monaco({pos}, {nam})")
		return (self.static_dir / "html" / "monaco.html").read_bytes()

	@cherrypy.expose
	@cherrypy.tools.json_out()
	def get_book_lst(self, * pos, ** nam) :
		return self.shelf.book_set

	def get_index(self, * pos, ** nam) :
		b = self.shelf[nam['b']]
		return

	@cherrypy.expose
	def _get_json(self, * pos, ** nam) :

		if 'b' not in nam or 'f' not in nam :
			raise cherrypy.HTTPError(400)

		if nam['b'] not in self.shelf.book_set :
			raise cherrypy.HTTPError(404)

		if '../' in nam['f'] :
			raise cherrypy.HTTPError(403)

		return self.proxy._get_json(nam['b'], nam['f'])

	@cherrypy.expose
	def _get_section(self, * pos, ** nam) :
		if 'b' not in nam or 's' not in nam :
			raise cherrypy.HTTPError(400)

		if nam['b'] not in self.shelf.book_set :
			raise cherrypy.HTTPError(404)

		return self.proxy._get_section(nam['b'], int(nam['s']))

		s = int(nam['s'])
		b = self.shelf[nam['b']]
		t = (b.base_dir / 'part' / f'{s:04d}').read_text()
		e = b.expand_shortcut(t)

		Path( b.base_dir / ".tmp" / f'{s:04d}.expanded.bkt').write_text(e)

		o = b.parse_section(e)

		g = oaktree.proxy.braket.BraketProxy()
		k = oaktree.proxy.braket.BraketProxy(indent='')

		g.save(o, Path( b.base_dir / ".tmp" / f'{s:04d}.parsed.bkt'))
		k.save(o, Path( b.base_dir / ".tmp" / f'{s:04d}.parsednoindent.bkt'))

		h = oaktree.Leaf('tmp')
		self.to_html5.compose(o, h)

		g.save(h.sub[0], Path( b.base_dir / ".tmp" / f'{s:04d}.composed.bkt'))
		k.save(h.sub[0], Path( b.base_dir / ".tmp" / f'{s:04d}.composednoindent.bkt'))

		f = oaktree.proxy.html5.Html5Proxy(indent='', fragment=True)
		f.save(h.sub[0], Path( b.base_dir / ".tmp" / f'{s:04d}.result.html'))

		return f.save(h.sub[0])


