#!/usr/bin/env python3

""" this class take a parsed marccup as an oaktree, and transform it into an html5 tree """

class AutomaticTitle() :
	def __init__(self, max_depth=6) :
		self.max_depth = max_depth
		self.reset()

	def __str__(self) :
		return '.'.join(str(i) for i in self.h if i != 0) + '.&nbsp;'

	def reset(self) :
		self.h =  [0,] * self.max_depth

	def increment(self, d) :
		self.h[d] += 1
		for i in range(d+1, 6) :
			self.h[i] = 0

class Html5Composer() :

	tr_map = {
		"paragraph" : "p",
		"alinea" : "span",
		"table_row" : "tr",
		"page": "article"
	}

	def __init__(self) :
		self.title_num = AutomaticTitle()

	def compose(self, src, dst) :
		# print(f"convert({src}, {dst})")
		if isinstance(src, str) :
			dst.add_text(src)
		else :
			for src_sub in src.sub :
				if isinstance(src_sub, str) :
					dst.add_text(src_sub)
				else :
					if src_sub.tag in self.tr_map :
						dst_sub = dst.grow(self.tr_map[src_sub.tag])
						self.compose(src_sub, dst_sub)
					elif hasattr(self, f"_compose_{src_sub.tag}") :
						getattr(self, f"_compose_{src_sub.tag}")(src_sub, dst)
					else :
						dst_sub = dst.grow(src_sub.tag)
						self.compose(src_sub, dst_sub)

	def compose(self, child_src, parent_dst) :
		if isinstance(child_src, str) :
			parent_dst.add_text(child_src)
		else :
			if child_src.tag in self.tr_map :
				# just a translation, easy, let's do that !
				sub_dst = parent_dst.grow(self.tr_map[child_src.tag],
					style=set(child_src.style)
				)
				sub_continue = True
			elif hasattr(self, f"_compose_{child_src.tag}") :
				# it has it special function, let's call it !
				sub_dst, sub_continue = getattr(self, f"_compose_{child_src.tag}")(child_src, parent_dst)
			else :
				# nothing of the above, just translate as this
				sub_dst = parent_dst.grow(child_src.tag)
				sub_continue = True

			# print(child_src, sub_dst, sub_continue)
			if sub_continue :
				for sub_src in child_src.sub :
					self.compose(sub_src, sub_dst)

	def _compose_title(self, src, dst) :
		d = len(src.ancestor_lst) - 3

		self.title_num.increment(d)

		sub_dst = dst.grow(f'h{d+1}').add_text(str(self.title_num))

		return sub_dst, True

	def _compose_quote(self, src, dst) :
		if 'block' in src.flag :
			sub_dst = dst.grow('blockquote')
		else :
			sub_dst = dst.grow('q')

		return sub_dst, True

	def _compose_book(self, src, dst) :
		return dst, True

	def _compose_math(self, src, dst) :
		if 'block' in src.flag :
			sub_dst = dst.grow('p', style={'math-block',})
		else :
			sub_dst = dst.grow('span', style={'math-inline',})

		sub_dst.add_text(''.join(src.sub))

		return sub_dst, False	

	def _compose_table_cell(self, src, dst) :
		if 'header' in src.flag :
			sub_dst = dst.grow('th')
		else :
			sub_dst = dst.grow('td')

		#for sub_src in src.sub :
		#	compose(sub_src, sub_dst)
			# sub_dst.add_text(''.join(src.sub))

		return sub_dst, True	
