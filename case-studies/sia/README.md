# Sia — a control client for a self-hosted Hermes agent

**Stack:** Kotlin, Jetpack Compose, Room, WebSocket JSON-RPC + REST, Gradle CI/release pipeline. Status: fork, hardened, verified on device; rework in progress (see "Rework").

## The problem

I run my own Hermes AI agent on a home server. The upstream project ships an Android control client, but it did not fit the way I wanted to drive the agent from a phone: I wanted voice input that behaves predictably (push-to-talk, never auto-send), a chat history that survives offline, and onboarding that assumes you already run Tailscale + Hermes on your system.

So I forked it, renamed it Sia (com.sia.hermescontrol), and hardened it.

## What was built

- **Jetpack Compose app, 30+ screens**: chat, cron job management, model selection, sidebars, settings, themes. Room holds local history so past conversations are available offline.
- **Transport**: WebSocket JSON-RPC for the live agent gateway, REST for CRUD (agent mailbox, cron, peers).
- **Voice, the hard part**:
  - the shipped on-device STT engine dead-locked on my devices — I documented two A/B attempts with the failure signatures, then removed the engine;
  - the final design is **push-to-talk → server-side Whisper (small, en-only) → transcript fills the compose box, never auto-sent**;
  - three PTT gestures, each tuned: hold ≥ 150 ms appends, swipe-up sends directly, drag-left cancels.
- **Release engineering**: full Gradle CI pipeline, signed release APKs, F-Droid metadata/fastlane.
- **Tests**: 2,495 tests passing across units and instrumentation at last full run.

## Screenshots

![](images/chat.png)
![](images/cron.png)
![](images/model.png)
![](images/sidebar-1.png)

## Rework (part of this case study, in progress)

The next iteration re-positions Sia as **"your Tailscale client for Hermes"**: if you already run Tailscale and Hermes on your system, this is your client. Concretely: a onboarding wizard that walks Tailscale-API-key → node discovery → first connection (instead of requiring the user to hand-copy connection settings), and trimming screens that don't fit that flow. The fork relationship is stated openly: this is upstream hermes-mobile, hardened for one specific operator flow.

## What I learned

- **Dead-locks beat error messages.** The STT engine failed with no output; reproducing the hang signatures in a controlled A/B was the only way to make the removal defensible.
- **Never auto-send voice.** Server-side transcription with the transcript in the compose box means the user confirms every message — a small UX constraint that eliminates the worst failure mode.
- **Instrumented tests on real hardware catch what units don't.** The gesture timings (150 ms hold, swipe thresholds) were tuned on device, against the emulator's soft keyboard and touch injection quirks.
- **CI for a fork is CI for upstream, plus secrets discipline.** Signing keys and API tokens live in the vault, never in the repo — the release pipeline references them, it doesn't contain them.

## Repo

Private fork (zifken/hermes-mobile) — rework lands on a branch, then publication decision.
