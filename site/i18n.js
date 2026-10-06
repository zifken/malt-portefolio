// FR/EN toggle — EN is the source in index.html; FR overrides here.
const I18N = {
  fr: {
    nav_projects: "Projets", nav_skills: "Compétences", nav_contact: "Contact",
    intro_h1: "Freelance IT & data",
    intro_p: "Je construis des pipelines et des outils data qui tiennent debout : Python, pandas, Streamlit, Neo4j, Linux. Derrière, dix ans d'exploitation IT (reconditionnement, homelab, automatisation) — et je livre de bout en bout : données en entrée, dashboard en sortie, documentation incluse.",
    projects_h2: "Projets choisis",
    decp_p: "Pipeline sur le jeu de données DECP (commande publique française, data.gouv.fr) : ingestion en Python stdlib avec watermark et dédoublonnage (~750 avis/semaine, champs remplis à ≥ 99,7 %), reconstruction quotidienne sur les fichiers consolidés 2019–2026 (1,36 M de contrats exploitables), dashboard Streamlit avec filtres CPV/département. Une sortie concrète : 55 957 contrats arrivant à échéance dans les 12 mois, filtrables par famille, département et acheteur — la fenêtre de re-tender. Cron hebdomadaire, moins de 2 h/semaine de calcul.",
    sia_p: "Fork du client Android officiel, durci pour un flux opérateur précis : 30+ écrans Jetpack Compose, transport WebSocket JSON-RPC + REST, historique hors-ligne en Room, pipeline de release signée avec métadonnées F-Droid. La voix est en push-to-talk uniquement : transcription Whisper côté serveur, le texte remplit la zone de saisie, jamais envoyé automatiquement. La STT embarquée d'origine dead-lockait — deux tentatives A/B documentées, puis retrait. 2 495 tests passants.",
    freebox_p: "Contrôle scriptable d'une Freebox : une bibliothèque de recettes éprouvées où chacune documente l'échec qu'elle a surmonté — la version de l'API n'est découverte que dans le JavaScript de l'appli web du routeur, les en-têtes CSRF documentés ne fonctionnent pas pour les POST de session (le contexte Ajax interne, oui), et un PUT partiel réinitialise silencieusement les champs omis de la config Wi-Fi. Inclut le listing LAN, le Wake-on-LAN et le diagnostic DFS (radar) de la bande 5 GHz.",
    kbtyp_p: "Un système documentaire basé sur Typst, défini une fois et instancié par livrable : système de page A4 avec titres numérotés, sommaire automatique, couverture, encadrés, tableaux thémés, blocs figures ; bilingue FR/EN depuis la même source ; figures générées en amont (plotnine) et référencées par chemin, pour qu'un rafraîchissement de données régénère le PDF à l'identique. Compilation en une commande, avec vérification bounding-box de chaque image et libellé avant livraison. Les livrables clients sont confidentiels ; un échantillon générique peut être produit sur demande.",
    skills_h2: "Compétences",
    skills_data: "Data : Python (pandas, plotnine), Streamlit, DuckDB/Parquet, Neo4j, pipelines et automatisation cron",
    skills_docs: "Documents : système PDF print-grade Typst, livrables bilingues FR/EN",
    skills_android: "Android : Kotlin, Jetpack Compose, Room, CI/release Gradle",
    skills_ops: "Ops : Linux, Podman, API routeur & homelab, Tailscale",
    skills_it: "IT : dix ans d'exploitation — reconditionnement, diagnostic, gestion de parc",
    contact_h2: "Contact",
    contact_p: "Email : kenziferaoun@proton.me",
    footer_note: "Site statique, sans traceur, sans étape de build."
  }
};
let lang = "en";
const btn = document.getElementById("lang");
function apply() {
  document.documentElement.lang = lang;
  btn.textContent = lang === "en" ? "FR" : "EN";
  if (lang === "en") {
    location.reload();
    return;
  }
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const v = I18N.fr[el.dataset.i18n];
    if (v) el.textContent = v;
  });
}
btn.addEventListener("click", () => { lang = lang === "en" ? "fr" : "en"; apply(); });
