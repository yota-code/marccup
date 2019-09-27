#!/usr/bin/env python3

from cc_pathlib import Path

import marccup

from oaktree.proxy.braket import BraketProxy

p = marccup.Parser()
m = p.parse_document(Path("./document"))

BraketProxy().save(m, Path("intermediate.bkt"))