# kb-typ — print-grade PDF deliverables from source

Typst, Python for asset generation, PDF output. In production use; the deliverables it produced are client work and are withheld here — no client content in this case study.

## The problem

Client work often needs more than a report: a print-grade A4 PDF with numbered headings, callout boxes, themed tables, figures, a cover, auto outline — bilingual FR/EN — produced from source, reproducible, revisable without desktop publishing software. Hand-writing it in a word processor doesn't scale and isn't versionable; generic report tools don't reach print quality.

## What I built

A Typst document system, defined once, instantiated per deliverable:

- Page system: A4, consistent margins, custom heading styles with automatic numbering, auto outline, cover page.
- Content primitives: callout blocks (info/warning), themed tables with striping, figure blocks with captions, code blocks.
- Bilingual FR/EN: language-keyed content, the same source compiles either way.
- Asset pipeline: figures are generated upstream (plotnine charts), referenced by path, so a data refresh regenerates the PDF with layout unchanged.
- Output: single-command compile to a print-ready PDF, checked for clipped text (bounding-box verification of every image and label) before delivery.

