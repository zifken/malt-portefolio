# Freebox control — the router as an API

Python (stdlib), HTTP API, cron. Runs on my home network. An operations case study, not a product.

## The problem

The Freebox (Free's ISP router) exposes an HTTP API for LAN listing, Wake-on-LAN, Wi-Fi and port management. Three quirks make real control painful:

- the API version is only discoverable from the web app's own JavaScript;
- session-auth POSTs via the documented CSRF headers do not work;
- Wi-Fi AP updates require full-record PUTs — send a partial record and the router silently resets the fields you omitted.

I wanted the router scriptable, like the rest of the homelab.

## What I built

A skills library of proven recipes, each documenting the failure it overcame, not just the working command:

- API path discovery: grep the router web app's freeboxos.min.js for the API version and endpoint map. The browser session is the ground truth for what the firmware actually serves.
- Session control: the proven path is a POST through the in-page Ext.Ajax context of the router web UI — the same request the UI itself issues.
- LAN host listing and Wake-on-LAN by MAC, with a parse step (MACs arrive HTML-anchored) so recipes are scriptable.
- Wi-Fi AP configuration: the PUT must carry the full record. A diagnostic recipe documents the partial-PUT reset behavior so it never bites again.
- DFS diagnosis: after a reboot the 5 GHz SSID can stay invisible because of dfs_cac (Dynamic Frequency Selection, radar-checking, up to 600 s). One recipe reads AP status, presence, dfs_cac status, and names that mode in one pass.

