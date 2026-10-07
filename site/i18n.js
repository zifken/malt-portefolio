// FR/EN toggle — FR is the source in index.html; EN overrides here. Default: FR.
const I18N = {
  en: {
    nav_projects: "The project", nav_contact: "Contact",
    projects_h2: "DECP Radar — analyses on French public procurement data",
        decp_p: "Pipeline over the DECP dataset (French public procurement, data.gouv.fr): stdlib-only ingestion with watermarking and dedupe (~750 notices/week, fields ≥ 99.7% filled), a daily rebuild over the consolidated 2019–2026 files (1.36 M usable contracts), and a Streamlit dashboard with CPV/department filters. One concrete output: 55,957 contracts expiring in the next 12 months, filterable by family, department and buyer — the re-tender window. Weekly cron, under 2 h/week of compute.",
    skills_h2: "Skills",
    skills_data: "Data: Python (pandas, plotnine), Streamlit, DuckDB/Parquet, pipelines & cron automation",
    skills_docs: "Deliverables: print-grade Typst PDF reports generated from the same data source, bilingual FR/EN",
    contact_h2: "Contact",
    contact_p: "Email: kenziferaoun@proton.me",
    contact_cta: "Half an hour is enough to scope your niche (CPV family, departments) and show the dashboard on your own criteria. Send me your sector and I will show you what it looks like.",
    footer_note: "Static site, no tracking, no build step.",
    footer_source: "Source on GitHub"
  }
};
let lang = "fr";
const btn = document.getElementById("lang");
function apply() {
  document.documentElement.lang = lang;
  btn.textContent = lang === "fr" ? "EN" : "FR";
  if (lang === "fr") {
    location.reload();
    return;
  }
  document.querySelectorAll("[data-i18n]").forEach(el => {
    if (!el.dataset.fr) el.dataset.fr = el.textContent.trim().replace(/\s+/g, " ");
    const v = I18N.en[el.dataset.i18n];
    if (v) el.textContent = v;
  });
  document.querySelectorAll("a[data-href-en]").forEach(el => {
    if (!el.dataset.hrefFr) el.dataset.hrefFr = el.getAttribute("href");
    el.setAttribute("href", lang === "en" ? el.dataset.hrefEn : el.dataset.hrefFr);
  });
}
btn.addEventListener("click", () => { lang = lang === "fr" ? "en" : "fr"; apply(); });
