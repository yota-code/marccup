#!/usr/bin/env python3

class Html5Composer_Scade() :

	def compose(self, child_src, parent_dst) :

		if hasattr(self, f"_compose_{child_src.tag}") :
			sub_dst, sub_continue = getattr(self, f"_compose_{child_src.tag}")(child_src, parent_dst)

		if sub_continue :
			for sub_src in child_src.sub :
				self.compose(sub_src, sub_dst)

		return sub_dst, sub_continue
	

	def _compose_const(self, src, dst) :
