# DECP Radar — analyses sur la commande publique française

Python (stdlib + pandas), Streamlit, Parquet, cron. Données data.gouv.fr (Licence Ouverte 2.0). Tourne chaque semaine sur un serveur maison.

## Le problème

Chaque marché public attribué en France doit être publié en avis DECP. Les données sont ouvertes mais éclatées en deux sources : fichiers delta quotidiens pour les avis frais, consolidations annuelles pour l'historique. Doublons, identifiants incohérents, montants qui changent de sens selon le type de marché. Toute question utile — qui a gagné quoi cette semaine, quels marchés arrivent à échéance — demande un pipeline avant une analyse.

## Ce que j'ai construit

Deux dépôts qui forment un seul produit.

decp-digest assure l'ingestion et le digest hebdomadaire. Python stdlib uniquement : récupération des deltas quotidiens, watermark sur le dernier fichier traité, dédoublonnage sur (acheteur.id, id) — environ 3% des enregistrements se répètent d'un fichier à l'autre. Mesuré sur une semaine de validation complète : ~750 avis, chaque champ utile du digest rempli à 99,7% ou mieux. Le README documente aussi ce que les données ne permettent pas, par exemple : la publication suit la notification avec une médiane de 6 jours, donc le digest groupe par date de publication.

decp-analytics reconstruit à partir des consolidés (2019–2026), écarte les enregistrements remplacés (311 002 écartés, 1 355 661 marchés exploitables), estime l'échéance comme dateNotification + dureeMois, et sort :

- la fenêtre de re-tender : 55 957 marchés arrivant à échéance dans les 12 mois, filtrables par famille CPV, département et acheteur ;
- un dashboard Streamlit (filtres CPV / département / période, KPI, vues acheteur et fournisseur) ;
- un échantillon public gratuit de 60 lignes.

Un cron le lundi 07:30 rafraîchit les deux couches. La reconstruction complète est la seule étape lourde et tient dans le budget de moins de 2 h/semaine.

## À partir des vraies données

![](../images/marches_par_annee.png)
![](../images/montants_par_annee.png)
![](../images/echeances_cpv.png)

*Graphique 3 — premières divisions CPV : 45 construction (19 916), 71 ingénierie (5 848), 79 conseil (2 658). Noms de divisions repris tels que publiés, non mappés (« 33 ? ») affichés tels quels.*

Tous les graphiques sortent de plotnine sur les sorties parquet du pipeline, et sont vérifiés programmatiquement (bounding boxes du texte) avant publication.

## Étude de cas — démonstration sur données publiques

*Étude de cas — démonstration sur données publiques (data.gouv.fr). Aucun client n'est cité ; les chiffres proviennent du pipeline DECP Radar et sont reproductibles.*

**Problème.** Les données DECP sont publiées en open data mais exploitables par presque personne : 1,36 M de contrats consolidés (2019–2026), ~750 avis nouveaux par semaine, champs hétérogènes. Un fournisseur qui veut repérer ses prochaines fenêtres de re-tender n'a ni le temps ni les outils pour trier ce volume.

**Approche.** Un pipeline Python (pandas, Parquet) : ingestion en stdlib avec watermark et déduplication, reconstruction quotidienne du jeu consolidé, contrôle de complétude des champs (≥ 99,7 % remplis). Au-dessus, un dashboard Streamlit avec filtres par famille CPV, département et acheteur. Un cron hebdomadaire tourne en moins de 2 h de calcul.

**Résultat.** Un chiffre d'appel concret : 55 957 contrats arrivent à échéance dans les 12 prochains mois, isolables par famille, territoire et acheteur. Le signal est exploitable en quelques minutes de filtrage au lieu de jours de tri manuel.

**Ce que le client en fait.** Une équipe commerciale ou un bureau d'études utilise ce point d'entrée pour identifier les marchés arrivant à terme dans sa zone, préparer la veille amont avant publication des avis, et prioriser ses démarches. Livrables possibles : le dashboard, une extraction périodique filtrée sur sa niche, ou un rapport PDF périodique généré depuis le même socle (Typst).

**Prochaine étape.** Une demi-heure d'échange suffit pour cadrer votre niche (CPV, départements) et voir le dashboard sur vos propres critères — contact : kenziferaoun@proton.me.

