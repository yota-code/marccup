#!/usr/bin/env python3

import sys

from cc_pathlib import Path

import oaktree.proxy.braket
import oaktree.proxy.html5

import marccup.parser.generic
import marccup.composer.html5

b = oaktree.proxy.braket.BraketProxy()

h_katex = '''<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>marccup with katex</title>

	<link href="https://fonts.googleapis.com/css2?family=Roboto+Slab&display=swap" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@500&display=swap" rel="stylesheet"> 

	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.css" integrity="sha384-bsHo4/LA+lkZv61JspMDQB9QP1TtO4IgOf2yYS+J6VdAYLVyx1c3XKcsHh0Vy8Ws" crossorigin="anonymous">
	<script src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.js" integrity="sha384-4z8mjH4yIpuK9dIQGR1JwbrfYsStrNK6MP+2Enhue4eyo0XlBDXOIPc8b6ZU0ajz" crossorigin="anonymous"></script>

	<link rel="stylesheet" href="../style.css">
</head>
<body>
<h2>Original marccup</h2>
<pre>{0}</pre>
<h2>Html preview</h2>
{3}
<h2>Parsed and converted tree</h2>
<table>
	<tr>
		<td><pre>{1}</pre></td>
		<td><pre>{2}</pre></td>
	</tr>
</table>

<script>
for (let h_block of document.querySelectorAll(".math-block")) {{
	console.log("block", h_block.textContent);
	katex.render(h_block.textContent.trim(), h_block, {{
    	throwOnError: false,
		displayMode: true
	}});
}}
for (let h_inline of document.querySelectorAll(".math-inline")) {{
	console.log("inline", h_inline.textContent);
	katex.render(h_inline.textContent.trim(), h_inline, {{
    	throwOnError: false,
		displayMode: false
	}});
}}
</script>
</body>
</html>'''


h_mathjax = '''<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>marccup with mathjax</title>
	<script id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
	<link href="https://fonts.googleapis.com/css2?family=Montserrat&family=Inconsolata&display=swap" rel="stylesheet"> 
	<link rel="stylesheet" href="../style.css">
	<script>

function mathjax_render(input, output, display) {{
	// https://mathjax.github.io/MathJax-demos-web/input-tex2svg.html
	output.innerHTML = '';
	
	// Reset the tex labels (and automatic equation numbers, though there aren't any here).
	MathJax.texReset();

	// Get the conversion options (metrics and display settings)
	var options = MathJax.getMetricsFor(output);
	options.display = display;

	MathJax.tex2svgPromise(input, options).then(function (node) {{
		output.appendChild(node);
	}}).catch(function (err) {{
		// If there was an error, put the message into the output instead
		output.appendChild(document.createElement('pre')).appendChild(document.createTextNode(err.message));
	}}).then(function () {{
		// do nothing
	}});
}}
	</script>
</head>
<body>
<h2>Original marccup</h2>
<pre>{0}</pre>
<h2>Html preview</h2>
{3}
<h2>Parsed and converted tree</h2>
<table>
	<tr>
		<td><pre>{1}</pre></td>
		<td><pre>{2}</pre></td>
	</tr>
</table>
<script>

for (let h_block of document.querySelectorAll(".math-block")) {{
	console.log(h_block.textContent);
	mathjax_render(h_block.textContent.trim(), h_block, true);
}}
for (let h_inline of document.querySelectorAll(".math-inline")) {{
	console.log(h_inline.textContent);
	mathjax_render(h_inline.textContent.trim(), h_inline, false);
}}

MathJax.startup.document.clear();
MathJax.startup.document.updateDocument();

</script>
</body>
</html>'''

def protect(s) :
	s = s.replace('<', '&lt;')
	s = s.replace('>', '&gt;')
	s = s.replace('\|', '&vert;')
	return s

for fnm in sys.argv[1:] :

	print(f"\x1b[31m{fnm}\x1b[0m")

	pth = Path(fnm).resolve()
	
	debug_dir = Path(f'./tmp-{pth.fname}')
	debug_dir.delete()

	u = marccup.parser.generic.GenericParser(debug_dir)
	m = pth.read_text()
	p = u.parse_auto(m)
	b.save(p, pth.with_suffix('.bkt'))

	v = marccup.composer.html5.Html5Composer()
	q = oaktree.Leaf('div')
	v.compose(p, q)

	g = oaktree.proxy.braket.BraketProxy()
	g.save(q.sub[0], debug_dir / "result.bkt")

	f = oaktree.proxy.html5.Html5Proxy(indent='', fragment=True)
	(debug_dir / 'result.mathjax.html').write_text(h_mathjax.format(
		protect(m), protect(g.save(p)), protect(g.save(q.sub[0])), f.save(q)
	))
	(debug_dir / 'result.katex.html').write_text(h_katex.format(
		protect(m), protect(g.save(p)), protect(g.save(q.sub[0])), f.save(q)
	))




