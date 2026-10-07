# kb-typ — print-grade PDF deliverables from source

**Stack:** Typst, Python (asset generation), PDF output. Status: system in use; the concrete deliverables it produced are client work and are **withheld** here — this case study describes the system and the method, with no client content.

## The problem

Client work often needs a deliverable that is more than a report: a print-grade A4 PDF with numbered headings, callout boxes, themed tables, SVG figures, a cover, auto outline — bilingual FR/EN — produced **from source**, reproducible, and revisable without desktop publishing software. Writing it by hand in a word processor doesn't scale and isn't versionable; generic report tools don't reach print quality.

## What was built

A Typst-based document system, defined once and instantiated per deliverable:

- **Page system**: A4, consistent margins, custom heading styles with automatic numbering, auto outline, cover page.
- **Content primitives**: callout blocks (info/warning), themed tables with striping, figure blocks with captions, code blocks.
- **Bilingual FR/EN**: language keyed content so the same source compiles either way — French labels/market material stays French, per the portfolio convention.
- **Asset pipeline**: figures are SVG/PNG generated upstream (e.g. plotnine charts), referenced by path, so a data refresh regenerates the PDF unchanged in layout.
- **Output**: single-command compile to a print-ready PDF, checked for **clipped text** (bounding-box verification of every image and label) before delivery.

## What I learned

- **Separate content from layout, for real.** With the primitives defined, a new deliverable is content work only — layout regressions stop happening.
- **Print quality is a layout budget.** Typst's deterministic layout (no reflow surprises) is what makes bounding-box verification of every figure meaningful.
- **Verification is part of the deliverable.** "Every image checked for clipped text before use" is a rule that applies to the pipeline's own charts too.
- **Reproducibility is the client deliverable.** The client gets a PDF plus the ability to regenerate it — that is worth more than a one-off file.

## Scope note

The system exists and is in production use. The specific deliverables it produced are client-confidential; on request, a generic sample document built with the same system can be produced and published.
