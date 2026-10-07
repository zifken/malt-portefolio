// FR/EN toggle — FR is the source in index.html; EN overrides here. Default: FR.
const I18N = {
  en: {
    nav_projects: "Projects", nav_skills: "Skills", nav_contact: "Contact",
    intro_h1: "I turn French public procurement data into tender opportunities",
    intro_p: "I build small, working data pipelines and tools: Python, pandas, Streamlit, Neo4j, Linux. Ten years of IT operations behind it (refurb, homelab, automation), and I ship the whole thing — data in, dashboard out, documented.",
    projects_h2: "Selected projects",
    decp_p: "Pipeline over the DECP dataset (French public procurement, data.gouv.fr): stdlib-only ingestion with watermarking and dedupe (~750 notices/week, fields ≥ 99.7% filled), a daily rebuild over the consolidated 2019–2026 files (1.36 M usable contracts), and a Streamlit dashboard with CPV/department filters. One concrete output: 55,957 contracts expiring in the next 12 months, filterable by family, department and buyer — the re-tender window. Weekly cron, under 2 h/week of compute.",
    sia_p: "Fork of the upstream Android client, hardened for one specific operator flow: 30+ Jetpack Compose screens, WebSocket JSON-RPC + REST transport, offline chat history in Room, signed release pipeline with F-Droid metadata. Voice is push-to-talk only: server-side Whisper transcription, transcript fills the compose box, never auto-sent. The shipped on-device STT dead-locked — two documented A/B attempts, then removal. 2,495 tests passing.",
    freebox_p: "Scriptable control of a Freebox ISP router: a library of proven recipes where each one documents the failure it overcame — the API version is only discoverable from the web app's own JavaScript, documented CSRF headers don't work for session POSTs (the in-page Ajax context does), and partial-record PUTs silently reset Wi-Fi AP fields. Includes LAN listing, Wake-on-LAN and DFS radar-check diagnosis for the 5 GHz band.",
    kbtyp_p: "A Typst-based document system, defined once and instantiated per deliverable: A4 page system with numbered headings, auto outline, cover, callout blocks, themed tables, figure blocks; bilingual FR/EN from the same source; figures generated upstream (plotnine) and referenced by path so a data refresh regenerates the PDF unchanged. Single-command compile, with bounding-box verification of every image and label before delivery. Client deliverables are withheld; the reusable template is public: zifken/typst-report-template.",
    skills_h2: "Skills",
    skills_data: "Data: Python (pandas, plotnine), Streamlit, DuckDB/Parquet, Neo4j, pipelines & cron automation",
    skills_docs: "Documents: Typst print-grade PDF system, bilingual FR/EN deliverables",
    skills_android: "Android: Kotlin, Jetpack Compose, Room, Gradle CI/release",
    skills_ops: "Ops: Linux, Podman, homelab & router APIs, Tailscale",
    skills_it: "IT: 10 years operations — refurb, diagnostics, fleet handling",
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
