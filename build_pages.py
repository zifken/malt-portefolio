#!/usr/bin/env python3
"""Build case-study HTML pages for the portfolio (run from repo root of malt-portefolio)."""
import re, pathlib

ROOT = pathlib.Path.cwd()

def md_inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"!\[\]\((.+?)\)", r'<img src="\1" alt="figure">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

def md_to_html(md):
    out, lines = [], md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## "):
            out.append(f"<h2>{md_inline(ln[3:])}</h2>")
        elif ln.startswith("# "):
            out.append(f"<h1>{md_inline(ln[2:])}</h1>")
        elif ln.startswith("### "):
            out.append(f"<h3>{md_inline(ln[4:])}</h3>")
        elif ln.strip().startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(f"<li>{md_inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r"^\d+\.\s", ln.strip()):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(f"<li>{md_inline(re.sub(r'^\d+\.\s', '', lines[i].strip()))}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        elif ln.startswith("![](") or (ln.startswith("*") and ln.endswith("*") and ln and not ln.startswith("**")):
            out.append(f"<p class='fig'>{md_inline(ln)}</p>")
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            t = "<table><tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in rows[0]) + "</tr>"
            for r in rows[1:]:
                t += "<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>"
            out.append(t + "</table>")
            continue
        elif ln.strip():
            out.append(f"<p>{md_inline(ln.strip())}</p>")
        i += 1
    return "\n".join(out)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Kenzi Feraoun</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<header>
  <nav>
    <span class="brand"><a href="../../">Kenzi Feraoun</a></span>
    <span class="spacer"></span>
    <a href="../../#projects">Projects</a>
    <a href="../../#contact">Contact</a>
  </nav>
</header>
<main>
{body}
</main>
<footer><span>Static site, no tracking.</span> · <a href="https://github.com/zifken/malt-portefolio">Source on GitHub</a></footer>
</body>
</html>
"""

CASES = {"decp": "DECP Radar", "sia": "Sia", "freebox-api": "Freebox control", "kb-typ": "kb-typ"}
for slug, title in CASES.items():
    d = ROOT / "case-studies" / slug
    md = (d / "README.md").read_text()
    body = md_to_html(md)
    (d / "index.html").write_text(PAGE.format(title=title, body=body))
    print(slug, "ok", len(body))
