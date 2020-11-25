#!/usr/bin/env python3


def find_all(txt, sub, offset=0) :
	sub_lst = list()
	i = txt.find(sub, 0)
	while i >= 0:
		sub_lst.append(i)
		i = txt.find(sub, i+1)
	return sub_lst

def jump_to_closing(txt) :
	d = 1
	for n, c in enumerate(txt) :
		if c == '<' :
			d += 1
		elif c == '>' :
			d -= 1
			if d == 0 :
				return n

def jump_to_closing_tag(txt, start) :
	d = 1
	n = start
	while True :
		c = txt[n]
		if c == '<'  :
			d += 1
		elif c == '>' :
			d -= 1
			if d == 0 :
				return n


def pick_higher(x_lst, p) :
	for x in x_lst :
		if p < x :
			return x
	return None

def trim_line(txt) :
	""" remove empty lines at the begining or at the end of a stack, in place """
	stack = txt.splitlines()
	while stack and not stack[0].strip() :
		stack.pop(0)
	while stack and not stack[-1].strip() :
		stack.pop(-1)
	return stack