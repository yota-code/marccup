#!/usr/bin/env python3


import threading

class ThreadSafeIdent() :
	def __init__(self, max_ident=0) :
		self.value = int(ident)
		self._lock = threading.Lock()
		
	def __enter__(self) :
		self._lock.acquire()
		return self
		
	def __exit__(self, type, value, traceback) :
		self._lock.release()

class ThreadSafeDict(dict) :
	def __init__(self, * p_arg, ** n_arg) :
		dict.__init__(self, * p_arg, ** n_arg)
		self._lock = threading.Lock()
		
	def __enter__(self) :
		self._lock.acquire(True)
		return self
		
	def __exit__(self, exc_type, exc_value, traceback) :
		self._lock.release()		

		
if __name__ == '__main__' :
	
	u = LockDict()
	
	with u as m :
		m[1] = 'foo'
	
	print(u)
		
		
	#def _acquire_file(self, root, ident, name) :
	#	"""
	#		root: top directory of the repository
	#		ident: ident of the file to lock
	#		name: name of th guy who requested it
	#		
	#		the lock will contain, for a given file, the name of the guy currently using in
	#	"""
	#	key = str(self.pth(ident).relative_to(root))
	#	with self._lock as m :
	#		if key not in m :
	#			m[key] = name
	#		return m[key]
	#	
	#def _release_file(self, root, ident, name) :
	#	key = str(self.pth(ident).relative_to(root))
	#	with self._lock as m :
	#		del m[key]
