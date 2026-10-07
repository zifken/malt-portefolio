# Freebox control — la box comme API

Python (stdlib), API HTTP, cron. Tourne sur mon réseau maison. Une étude de cas côté ops, pas un produit.

## Le problème

La Freebox expose une API HTTP : listing LAN, Wake-on-LAN, Wi-Fi, ports. Trois pièges rendent le contrôle réel pénible :

- la version de l'API ne se découvre que dans le JavaScript de la web-app de la box ;
- les POST de session avec les en-têtes CSRF documentés ne fonctionnent pas ;
- la config Wi-Fi exige des PUT avec l'enregistrement complet — un PUT partiel réinitialise silencieusement les champs omis.

Je voulais la box pilotable par script, comme le reste du homelab.

## Ce que j'ai construit

Une bibliothèque de recettes éprouvées, où chacune documente l'échec qu'elle a surmonté, pas seulement la commande qui marche :

- Découverte des chemins d'API : grep du freeboxos.min.js de la web-app pour la version de l'API et la carte des endpoints. La session navigateur est la vérité terrain sur ce que le firmware sert réellement.
- Contrôle de session : le chemin qui marche est un POST via le contexte Ext.Ajax interne de la web-app — la même requête que l'UI elle-même émet.
- Listing des hôtes LAN et Wake-on-LAN par MAC, avec une étape de parsing (les MAC arrivent ancrées en HTML) pour que les recettes soient scriptables.
- Configuration Wi-Fi : le PUT doit porter l'enregistrement complet. Une recette de diagnostic documente le comportement de remise à zéro du PUT partiel, pour que ça ne morde plus.
- Diagnostic DFS : après un reboot, le SSID 5 GHz peut rester invisible à cause de dfs_cac (Dynamic Frequency Selection, vérification radar, jusqu'à 600 s). Une recette lit l'état de l'AP, la présence, dfs_cac, et nomme ce mode en un passage.

## Détails

- Page en français : [./](./)
- English page: [../](../)

Petit, personnel, honnête : une victoire d'ops homelab. Les recettes tournent en cron pour les checks Wi-Fi, à la demande pour le WoL et les audits LAN.
