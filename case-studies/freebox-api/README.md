# Freebox control — driving a French ISP router through its API

**Stack:** Python (stdlib, via a skills library), HTTP API, cron. Status: running on my home network. This is an operations case study, not a product.

## The problem

The Freebox (Free's ISP router) exposes an HTTP API for LAN listing, Wake-on-LAN, Wi-Fi and port management. But three practical quirks make real control painful: the API version is only discoverable from the web app's own JavaScript; session-auth POSTs via documented CSRF headers do not work; and Wi-Fi AP updates require full-record PUTs — send a partial record and the router silently resets the fields you omitted.

I wanted the router to be manageable by script, the same way the rest of the homelab is.

## What was built

A skills library of **proven recipes** (each recipe documents the failure it overcame, not just the working command):

- **API path discovery**: grep the router web app's `freeboxos.min.js` for the API version and endpoint map — the browser session is the ground truth for what the firmware actually serves.
- **Session control**: after verifying that the documented CSRF-token headers don't work for session POSTs, the proven path is a POST **through the in-page `Ext.Ajax`** context of the router web UI — the same request the UI itself issues.
- **LAN host listing** and **Wake-on-LAN** by MAC, with a parse step (MACs arrive HTML-anchored) so recipes are scriptable.
- **Wi-Fi AP configuration**: PUT must carry the **full record** — a diagnostic recipe documents the partial-PUT reset behavior so it never bites again.
- **DFS diagnosis**: after a reboot the 5 GHz SSID can stay invisible because of `dfs_cac` (Dynamic Frequency Selection, radar-checking; can hold up to 600 s). The diagnostic recipe reads AP status, presence, `dfs_cac` status and identifies that mode in one pass.
- **API version discovery recipe** as the entry point for everything above.

## What I learned

- **Document the failure, then the command.** "CSRF headers don't work — use the in-page session path" is worth more than the working command alone; recipes that only show the happy path break on the next firmware update.
- **PUT semantics bite.** Partial-record PUTs on the AP endpoint silently reset omitted fields; full-record with explicit values is the only safe shape.
- **The router's web app is the API reference.** When the docs and the firmware disagree, the JS shipped in the web UI is the truth.
- **Radar-awareness is a feature, not a bug.** 5 GHz invisibility after reboot is usually DFS radar-checking — reading `dfs_cac` status turns "my Wi-Fi is broken" into "the channel is in its check window".

## Scope

Small, personal, and honest: this is a homelab operations win, not a product. The recipes run on cron for Wi-Fi checks and are invoked on demand for WoL and LAN audits.
