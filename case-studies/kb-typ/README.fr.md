# kb-typ — livrables PDF print-grade depuis une source

Typst, Python pour la génération des assets, sortie PDF. En usage réel ; les livrables produits sont du travail client et sont retenus ici — aucun contenu client dans cette étude de cas.

## Le problème

Le travail client demande souvent plus qu'un rapport : un PDF A4 print-grade avec titres numérotés, encadrés, tableaux thémés, figures, couverture, sommaire automatique — bilingue FR/EN — produit depuis une source, reproductible, révisable sans logiciel de PAO. L'écrire à la main dans un traitement de texte ne passe pas à l'échelle et n'est pas versionnable ; les outils de rapport génériques n'atteignent pas la qualité print.

## Ce que j'ai construit

Un système documentaire Typst, défini une fois, instancié par livrable :

- Système de page : A4, marges constantes, styles de titres personnalisés avec numérotation automatique, sommaire automatique, page de couverture.
- Primitives de contenu : encadrés (info/warning), tableaux thémés avec striping, blocs figures avec légendes, blocs code.
- Bilingue FR/EN : contenu indexé par langue, la même source compile dans les deux langues.
- Pipeline d'assets : les figures sont générées en amont (graphiques plotnine), référencées par chemin, pour qu'un rafraîchissement de données régénère le PDF sans changer la mise en page.
- Sortie : compilation en une commande vers un PDF prêt à imprimer, vérifié pour le texte coupé (bounding-box de chaque image et libellé) avant livraison.

## Détails

- Page en français : [./](./)
- English page: [../](../)

Le système est en usage réel. Les livrables concrets sont confidentiels ; sur demande, un document d'exemple générique construit avec le même système peut être produit.
