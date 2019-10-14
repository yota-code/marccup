#!/usr/bin/env python3

import io
import pathlib

def auto_write(func) :
	"""
	auto_write is a decorator, for decoracted composer, the auto_write _aw argument
	will be replaced by the most adequate output way (file, stream, etc.)
	
	"""
	def decorator(* pos, _aw=None, ** nam) :
		if _aw is None :
			# return as a str()
			fid = io.StringIO()
			func(* pos, _aw=fid.write, ** nam)
			return fid.getvalue()
		if hasattr(_aw, "write") :
			# write into _aw.write()
			func(* pos, _aw=_aw.write, ** nam)
		elif isinstance(_aw, str) :
			# write to the file
			with pathlib.Path(_aw).open('wt', encoding='utf8') as fid :
				func(* pos, _aw=fid.write, ** nam)
		elif isinstance(_aw, pathlib.Path) :
			# write to the path
			with _aw.open('wt', encoding='utf8') as fid :
				func(* pos, _aw=fid.write, ** nam)
		else :
			# write into _aw.write()
			func(* pos, _aw=_aw, ** nam)
		return None
	return decorator
	
def auto_read(p) :
	""" return the full content of p, be it a string, a file or anything else with a read() method """
	if isinstance(p, pathlib.Path) :
		with p.open('rt', encoding='utf8') as fid :
			return fid.read()	
	elif isinstance(p, str) :
		return p
	else :
		return p.read()
		
if __name__ == '__main__' :
	
	@auto_write
	def tst_sub(s, _aw=None) :
		_aw(str(len(s)) + ".")
	
	@auto_write
	def tst_main(s, _aw=None) :
		_aw("START"+s+"END/")
		tst_sub(s, _aw=_aw)
	
	print("<"+tst_main("middle")+">")
	

