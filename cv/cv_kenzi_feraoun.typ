// CV — Kenzi Feraoun, version data (portfolio). FR.
#set page(paper: "a4", margin: (x: 1.7cm, y: 1.4cm))
#set text(font: "DejaVu Sans", size: 9.1pt, lang: "fr")
#set par(justify: false, leading: 0.55em)

#let job(when, title, place) = grid(
  columns: (4.3cm, 1fr), column-gutter: 10pt,
  [#text(size: 8.2pt, fill: rgb("#555"), when)],
  [*#title* — #text(size: 8.8pt, fill: rgb("#555"), place)]
)
#let sec(t) = block(above: 10pt, below: 5pt)[
  #text(size: 10.5pt, weight: 700, fill: rgb("#0b5394"), tracking: 0.05em)[#upper(t)]
  #v(-5pt);#line(length: 100%, stroke: 0.5pt + rgb("#0b5394"))
]

#align(center)[
  #text(size: 17pt, weight: 700)[Kenzi Feraoun]
  #v(2pt)
  #text(size: 10.5pt, fill: rgb("#555"))[Consultant informatique & data — PME : systèmes, réseaux, données]
  #v(2pt)
  #text(size: 8.8pt, fill: rgb("#555"))[Malakoff (92) · 06 95 59 28 81 · kenziferaoun\@proton.me · zifken.github.io/malt-portefolio]
]

== Profil
Consultant informatique pour des PME depuis 2019 : installations, réseaux, gestion de parc, sauvegardes, solutions d'auto-hébergement — avec une spécialisation data de bout en bout (pipelines, qualité mesurée, dashboards). Bagage scientifique (M1 chimie, Sorbonne Université). Je mets en place des systèmes qui tiennent en production, documentés, récupérables.

#sec[Expériences]

#job[Mai 2026 – aujourd'hui][Technicien informatique (reconditionnement)][Furb, Montreuil]
- Diagnostic et remise en état de parcs ; effacement certifié des disques ; suivi des données de process.
- Automatisation : scripts d'audit et de traçabilité (Python, Linux).

#job[Sept. 2025 – juin 2026][Enseignant en programmation][Funtech Adventure, Paris]
- Ateliers hebdomadaires de code (6–10 ans) dans plusieurs écoles (École Jeannine Manuel, Union School) ; coordination avec les équipes pédagogiques.

#job[Depuis 2019][Consultant informatique & data — PME][Indépendant, Paris]
- *Infra & exploitation* : installation et déploiement de postes et serveurs Linux/Windows, réseaux locaux (câblage, Wi-Fi, VPN inter-sites), gestion de parc et ticketing (GLPI : inventaire, masterisation, renouvellement).
- *Continuité* : mise en place de solutions de sauvegarde automatisées avec restauration testée ; auto-hébergement de services (Nextcloud, fichiers, agendas).
- *Data* : reporting et pipelines Python pour PME ; pipeline DECP (commande publique, data.gouv.fr) — ingestion stdlib (~750 avis/semaine, champs remplis à 99,7%), consolidation 2019–2026 (1,36 M de marchés), dashboard Streamlit.
- *Développement* : contrôle d'une Freebox par API, watchdogs, client mobile Android (fork Kotlin, 2 495 tests passants) ; chaîne d'autoédition de documents Typst (PDF print-grade, FR/EN).
- *Web* : sites et outils internes pour PME — backends Flask/Django, frontends htmx/Vue, de la maquette à la mise en ligne.
- Dépannage, formation et conseil utilisateurs.

#job[Mai – juil. 2019][Stagiaire en recherche][Lab. de Chimie Théorique, Sorbonne Université]
- Analyse DFT de molécules radicalaires ; interfaces graphiques et traitements de données pour un simulateur de réactions adiabatiques.

#job[2019 – 2022][Animateur pédagogique et aide aux devoirs][ALEM / centre de loisirs, Paris / Montrouge]
- Activités maths/informatique (Scratch), suivi personnalisé d'élèves de primaire.

#sec[Formation]

#job[2020 – 2022][Master 1 Chimie (parcours analytique, physique et théorique)][Sorbonne Université, Paris]

#job[2017 – 2020][Licence de Chimie][Sorbonne Université, Paris]

#sec[Compétences]
- *Infra* : réseaux LAN/VPN, gestion de parc (GLPI), ticketing, sauvegardes/restauration, auto-hébergement (Nextcloud)
- *Ops* : Linux, Podman, API routeur/homelab, Tailscale, Git
- *Data* : Python (pandas, plotnine), SQL/PostgreSQL, Streamlit, DuckDB/Parquet, Neo4j, cron
- *Web* : Flask, Django, htmx, Vue, HTML/CSS/JS
- *Docs* : Typst (PDF print-grade, bilingue FR/EN)
- *Android* : Kotlin, Jetpack Compose, Room, CI Gradle

#sec[Langues]
Français langue maternelle · Anglais courant
