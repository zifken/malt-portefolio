// CV — Kenzi Feraoun, version data (portfolio). FR.
#set page(paper: "a4", margin: (x: 1.7cm, y: 1.7cm))
#set text(font: "DejaVu Sans", size: 9.4pt, lang: "fr")
#set par(justify: false, leading: 0.62em)

#let job(when, title, place) = grid(
  columns: (4.3cm, 1fr), column-gutter: 10pt,
  align(right)[#text(size: 8.2pt, fill: rgb("#555"), when)],
  [*#title* — #text(size: 8.8pt, fill: rgb("#555"), place)]
)
#let sec(t) = block(above: 10pt, below: 5pt)[
  #text(size: 10.5pt, weight: 700, fill: rgb("#0b5394"), tracking: 0.05em)[#upper(t)]
  #v(-5pt);#line(length: 100%, stroke: 0.5pt + rgb("#0b5394"))
]

#align(center)[
  #text(size: 17pt, weight: 700)[Kenzi Feraoun]
  #v(2pt)
  #text(size: 10.5pt, fill: rgb("#555"))[Data & IT — pipelines, outils, dashboards]
  #v(2pt)
  #text(size: 8.8pt, fill: rgb("#555"))[Malakoff (92) · 06 95 59 28 81 · kenziferaoun\@proton.me · zifken.github.io/malt-portefolio]
]

== Profil
Construction de pipelines de données et d'outils qui tiennent debout : ingestion, qualité mesurée, dashboards, documentation. Bagage scientifique (chimie, niveau M1, Sorbonne Université) et dix ans d'exploitation IT (reconditionnement, homelab, automatisation). Je livre de bout en bout : données en entrée, dashboard en sortie.

#sec[Expériences]

#job[Mai 2026 – aujourd'hui][Technicien informatique (reconditionnement)][Furb, Montreuil]
- Diagnostic et remise en état de parcs ; effacement certifié des disques ; suivi des données de process.
- Automatisation : scripts d'audit et de traçabilité (Python, Linux).

#job[Sept. 2025 – juin 2026][Enseignant en programmation][Funtech Adventure, Paris]
- Ateliers hebdomadaires de code (6–10 ans) dans plusieurs écoles (École Jeannine Manuel, Union School) ; coordination avec les équipes pédagogiques.

#job[Depuis 2019][Consultant informatique & data][Indépendant, Paris]
- Pipeline DECP (commande publique, data.gouv.fr) : ingestion stdlib (~750 avis/semaine, champs remplis à 99,7%), reconstruction consolidée 2019–2026 (1,36 M de marchés), fenêtre de re-tender de 55 957 marchés, dashboard Streamlit.
- Outils homelab : contrôle d'une Freebox par API, watchdogs, clients mobiles (fork Android Kotlin, 2 495 tests passants).
- Système documentaire Typst : PDF print-grade bilingues FR/EN générés depuis la source.
- Dépannage, formation et conseil (public 21–79 ans).

#job[Mai – juil. 2019][Stagiaire en recherche][Lab. de Chimie Théorique, Sorbonne Université]
- Analyse DFT de molécules radicalaires ; interfaces graphiques et traitements de données pour un simulateur de réactions adiabatiques.

#job[2019 – 2022][Animateur pédagogique et aide aux devoirs][ALEM / centre de loisirs, Paris / Montrouge]
- Activités maths/informatique (Scratch), suivi personnalisé d'élèves de primaire.

#sec[Formation]
#job[2020 – 2022][Master 1 Chimie (parcours analytique, physique et théorique)][Sorbonne Université, Paris]
#job[2017 – 2020][Licence de Chimie][Sorbonne Université, Paris]

#sec[Compétences]
- *Data* : Python (pandas, plotnine), Streamlit, DuckDB/Parquet, Neo4j, SQL, cron
- *Docs* : Typst (PDF print-grade, bilingue FR/EN)
- *Android* : Kotlin, Jetpack Compose, Room, CI Gradle
- *Ops* : Linux, Podman, API routeur/homelab, Tailscale, Git

#sec[Langues]
Français langue maternelle · Anglais courant
