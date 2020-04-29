#!/usr/bin/env python3

import sys

from cc_pathlib import Path

import oaktree
import marccup

section_name = sys.argv[1]
section_pth = Path("document") / f"{section_name}.bkt"
section_txt = section_pth.read_text()

u = marccup.Parser(debug_dir=Path("tmp"))
p = oaktree.Leaf("section")
u.parse_section(p, section_txt)

v = marccup.Composer(p, Path("tmp/result.html"))


