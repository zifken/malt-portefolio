"""Rebuild DECP charts with programmatic text audit (overlap/clipping)."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from plotnine import *

SRC = "/home/kz/src/decp-analytics/data"
OUT = "/home/kz/src/portfolio/case-studies/decp/images"
os.makedirs(OUT, exist_ok=True)

BASE = theme_minimal(base_family="DejaVu Sans", base_size=12) + theme(
    plot_title=element_text(size=14, face="bold"),
    plot_subtitle=element_text(size=10, color="#555555"),
    axis_title=element_text(size=11),
)

plots = {}

m = pd.read_parquet(f"{SRC}/marches.parquet",
                    columns=["date_notification", "montant", "cpv_div", "departement"])
m["annee"] = pd.to_datetime(m["date_notification"], errors="coerce").dt.year
m = m[m["annee"].between(2019, 2026)]
per_year = m.groupby("annee").agg(n=("montant", "size"),
                                  total_md=("montant", lambda s: s.sum() / 1e9)).reset_index()

plots["marches_par_annee"] = (ggplot(per_year, aes(x="factor(annee)"))
    + geom_col(aes(y="n"), fill="#1f3b57", width=0.7)
    + geom_text(aes(y="n", label="n"), va="bottom", size=9, format_string="{:,.0f}", nudge_y=per_year["n"].max()*0.02)
    + scale_y_continuous(labels=lambda l: [f"{float(x)/1000:.0f} k" if float(x) >= 1000 else f"{x:.0f}" for x in l],
                         expand=(0, 0.08))
    + labs(title="Marchés notifiés par année dans la base DECP consolidée",
           subtitle="Après dédoublonnage — 1 355 661 marchés utilisables (2019–2026), fichiers consolidés data.gouv.fr",
           x="Année de notification", y="Nombre de marchés")
    + BASE)

plots["montants_par_annee"] = (ggplot(per_year, aes(x="factor(annee)", y="total_md"))
    + geom_col(fill="#2e6f4e", width=0.7)
    + geom_text(aes(y="total_md", label="total_md"), va="bottom", size=9,
                format_string="{:,.1f}", nudge_y=per_year["total_md"].max()*0.02)
    + scale_y_continuous(expand=(0, 0.08))
    + labs(title="Volume total notifié par année",
           subtitle="Somme des montants (milliards d'euros) — montants d'engagement, pas de dépense réelle",
           x="Année de notification", y="Montant total (Md EUR)")
    + BASE)

e = pd.read_csv(f"{SRC}/expiries_upcoming.csv")
g = (e.groupby("cpv_div").agg(n=("id", "size"), total=("montant", lambda s: s.sum() / 1e9))
     .reset_index().nlargest(10, "n"))
g["lab_n"] = g["n"].map(lambda v: f"{v/1000:.1f}k")
SHORT = {
    "Travaux de construction": "Travaux",
    "Services d'architecture et ingénierie": "Ingénierie",
    "Conseil, marketing, recrutement": "Conseil",
    "Déchets, environnement": "Environnement",
    "Réparation et entretien": "Réparation",
    "Transports": "Transports",
}
g["div_code"] = g["cpv_div"].map(lambda v: SHORT.get(v, v))  # short label; raw division codes stay as-is
plots["echeances_cpv"] = (ggplot(g, aes(x="reorder(div_code, -n)", y="n"))
    + geom_col(fill="#1f3b57", width=0.7)
    + geom_text(aes(y="n", label="lab_n"), va="bottom", size=8,
                format_string="", nudge_y=g["n"].max()*0.02)
    + scale_y_continuous(labels=lambda l: [f"{float(x)/1000:.0f} k" if float(x) >= 1000 else f"{x:.0f}" for x in l],
                         expand=(0, 0.1))
    + labs(title="Échéances à venir dans les 12 mois, par division CPV (top 10)",
           subtitle="55 957 marchés en fenêtre de re-tender probable (6 à 12 mois)",
           x="Division CPV", y="Nombre de marchés")
    + BASE)
print(g[["cpv_div", "n"]].to_string(index=False))


def audit(fig):
    """Return list of problems: text outside figure, or pairwise overlaps."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.get_size_inches() * fig.dpi
    texts = [t for ax in fig.axes for t in ax.texts + [ax.title, ax._left_title if hasattr(ax, "_left_title") else ax.title] + ax.get_xticklabels() + ax.get_yticklabels() if t.get_text()]
    probs = []
    boxes = []
    for t in texts:
        try:
            bb = t.get_window_extent(renderer=r)
        except Exception:
            continue
        if bb.x0 < -2 or bb.y0 < -2 or bb.x1 > W + 2 or bb.y1 > H + 2:
            probs.append(f"OUT-OF-BOUNDS: {t.get_text()!r} bbox={bb}")
        boxes.append((t.get_text(), bb))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            ox = min(a.x1, b.x1) - max(a.x0, b.x0)
            oy = min(a.y1, b.y1) - max(a.y0, b.y0)
            if ox > 3 and oy > 3:
                probs.append(f"OVERLAP: {boxes[i][0]!r} vs {boxes[j][0]!r} ({ox:.0f}x{oy:.0f}px)")
    return probs


report = {}
import fitz  # PyMuPDF
import math
for name, p in plots.items():
    png = f"{OUT}/{name}.png"
    pdf = f"{OUT}/{name}.pdf"
    p.save(png, width=9, height=5, dpi=170)
    p.save(pdf, width=9, height=5)
    doc = fitz.open(pdf)
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    words = page.get_text("words")  # x0,y0,x1,y1,word,block,line,word_no
    probs = []
    # out of page bounds
    for w in words:
        x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
        if x0 < -0.5 or y0 < -0.5 or x1 > W + 0.5 or y1 > H + 0.5:
            probs.append(f"OUT: {txt!r} at ({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}) page=({W:.0f}x{H:.0f})")
    # pairwise word-box overlap (same-line words are adjacent, so filter tiny overlaps)
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            a, b = words[i], words[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 1 and oy > 1:
                probs.append(f"OVERLAP: {a[4]!r} vs {b[4]!r} ({ox:.1f}x{oy:.1f}pt)")
    doc.close()
    from PIL import Image
    im = Image.open(png)
    report[name] = f"png {im.size}px; page {W:.0f}x{H:.0f}pt; words={len(words)}; {len(probs)} problem(s)"
    for pr in probs[:20]:
        report[name] += "\n  " + pr
    import os
    os.remove(pdf)

for k, v in report.items():
    print(k, "->", v)
