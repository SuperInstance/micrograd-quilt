# zcode 0.16.9 — `remote exec` dropped: verified + alternate paths

Date: 2026-10-03 (snowball pulse, queue item #10)
Question: is `zcode remote exec` still available in 0.16.9, and what is the
alternate remote path, before any exp003 relaunch on a zcode substrate?

## Verdict

**`remote exec` is GONE in zcode 0.16.9.** Verified empirically on this host
(install: `zcode-app-cli 3.14.4-30` npm wrapper, `zcode-runtime 0.16.9`):

- `zcode --help` command list (receipt: `zcode-help-0.16.9.txt`):
  `app-server`, `commands`, `doctor`, `login`, `logout`, `plugins`, `skills`,
  `tui`, `version`. **No `remote` subcommand exists.**
- `zcode remote exec --help` (receipt: `zcode-remote-exec-help.txt`) does NOT
  error — the parser silently falls through to the general help text. Absence
  is silent, not refused; a script keying on exit codes would not notice.
- Official changelog page (https://zcode.z.ai/en/changelog) covers the desktop
  app v3.x line only; **no CLI-runtime changelog is published** — version
  history for 0.16.x must be read from the binary itself + third-party docs.

## What replaced it (alternate remote paths)

Remote access moved OUT of the CLI into the third-party ACP bridge
(`william0wang/zcode-acp`, fetched 2026-10-03, docs/REMOTE.md + README):

1. **ACP bridge + hub daemon** (`zcode-acp-server`): bridges expose an ACP
   endpoint; a machine-level hub (default `127.0.0.1:8377`) adds token auth,
   instance discovery (`GET /api/instances`), and WebSocket proxying; a
   ready-made phone/web client exists (zcode-acp-remote).
2. **Remote session-create** (ADR-0014): `POST /api/instances
   {workspacePath}` incubates a session with no editor required; headless/
   SSH hosts fall back to detached `zcode-acp serve` (or
   `remote.terminal.enabled: false`).
3. **>=0.16.0 upstream removals** (bridge CHANGELOG, pinned): `session/steer`,
   `session/rewind`, `session/rewindCascade` + `/steer`, `/rewind` slash
   commands dropped upstream — moved to the v4 conversation API. Bridge
   aligned with the open-sourced ZCode backend at 0.16.9.
4. **Local in-process paths that remain**: `zcode -p "<prompt>"` headless
   single-prompt (the mode all prior zcode lanes used), `zcode app-server`
   (ZCode Protocol stdio server), `--resume sess_…` / `-c`.

## Recommendation for exp003 relaunch

- Do NOT block exp003 on `remote exec` — it no longer exists; any lane doc
  referencing it is stale.
- Fleet already switched substrate zcode→kimi-code by Kimi directive
  (07:12 10/2) after repeated service-side "Turn was cancelled"; zcode stays
  fallback-only. If a zcode lane IS relaunched: use `zcode -p` in-turn via
  setsid launcher scripts (doctrine from 10/2: no tmux on critical path,
  everything in-turn or nothing), or `zcode-acp serve` where a persistent
  addressable session is truly needed.
- Silent-fallback gotcha pinned: zcode's parser prints general help with exit
  0 for unknown subcommands — lane wrappers must grep the help text for the
  command name, not trust exit codes.

## Honest limits

- No official 0.16.x release notes exist to cite; verdict rests on the
  installed binary's own help output + the ACP bridge's maintained docs.
- Not installed/tested: `zcode-acp-server` itself (npm package not pulled);
  hub/session-create paths described from fetched docs, not executed.
- The 0.16.9 build here may lag the latest runtime; `zcode doctor` shows
  artifact `node-bundle`, sea: no.
