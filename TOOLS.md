# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Environment facts (this host)

- **Host:** Aliyun (iZt4n0faw77uvkphcb06ecZ), Linux, python 3.12, node v24.
- **pip is mirror-pinned:** `/etc/pip.conf` sets `index-url=http://mirrors.cloud.aliyuncs.com/pypi/simple/` — the Aliyun mirror **lags pypi.org by minutes**. When verifying fresh uploads/installs, always use `-i https://pypi.org/simple` explicitly. (Lesson: RD-001 verification 2026-10-03 — pip said "no matching distribution" while PyPI JSON + simple index were already live.)
- **pip installs need a venv:** host is PEP 668 externally-managed; `pip install` fails without a venv (or `--break-system-packages`). Use `python3 -m venv /tmp/<name>-venv`.
- **gh CLI:** authenticated as SuperInstance (`/usr/bin/gh`, token `gho_*`). Restored 2026-10-03 after key rotation. Push access works.
- **PyPI:** `~/.pypirc` carries a `__token__` for the SuperInstance PyPI account (maintainer credential, dropped by user 2026-10-03). Mode 600. If twine says "Malformed configuration", check for duplicate sections (user appended one once; I deduped; user then removed a stray `pypi-` section — currently one clean `[pypi]` section, verified parsing 06:24Z).
- **fleet-witness key:** `~/.config/fleet-witness/key.pem` (Ed25519, 0600; pubkey `key.pub`, committed to SuperInstance/fleet-witness-checkpoints as `KEYS/openclaw-main.pub`). Created 2026-10-04 for the L2 anchor channel. Include in key rotation.
- **Witness repo:** SuperInstance/fleet-witness-checkpoints (private) — anchored fleet checkpoints; audit reads `checkpoints/<slug>/LATEST`, pins (size, root).
- **Cloudflare:** `/root/.env` holds `CF_TOKEN` (rotated, dropped by user 2026-10-03T06:33Z) — verified valid/active against `api.cloudflare.com/client/v4/user/tokens/verify`, account `049ff5e8…` (Casey.digennaro@gmail.com's Account). Scope confirmed working for reads (account info; both workers live: quilt-tip-notary + organ-watcher). Wrangler-ready: `export CF_API_TOKEN=$(grep -oP 'CF_TOKEN=\K.*' /root/.env)`.
- **Minimax:** `/root/.env` `MINIMAX_TOKEN` — verified 2026-10-03: `/v1/models` 200 (MiniMax-M3, M2.7), chat round-trip OK. Base `https://api.minimax.io/v1` (OpenAI-compatible). Some endpoints may want a GroupId header (unverified).
- **JEV/Typesafe:** REVOKED by Casey 2026-10-06 (~02:45 CST). `TYPESAFE` in `/root/.env` is a DEAD token — do not attempt R6 live batteries until Casey drops a fresh key. All jev-quilt R6 run-3..run-6 work (PRs #50–#53) is MERGED; record-only findings live in `docs/R6_RUN*_PROBES.md` + receipts 010–015.
- **MothQuantum:** REVOKED by Casey 2026-10-06 (~02:45 CST). `MOTHQUANTUM_TOKEN` in `/root/.env` is DEAD. Simulator-side quantum lanes (MicroMoth IonQ ladder) need no key; hardware rung-3 is gated anyway.
- **MothQuantum (REVOKED 2026-10-06):** was live 2026-10-03 per docs Casey supplied: base `https://api.mothquantum.com/api/v1`, Bearer auth, async jobs. History: `coin-toss-v1` + `comet-qrng-v1` completed with receipts; `mode:"emu"`=Aer baseline; `"qpu"`+BYO IBM token=hardware. Docs: https://docs.mothquantum.com/docs/intro — RE-VERIFY with a fresh key before citing as live.
- **GitHub PAT:** `/root/.env` `GITHUB` (`ghp_…`) — verified login SuperInstance. (gh CLI uses its own `gho_` token; both work.)
- **AI-Writings is ~3.6GB** — do NOT clone on this host (OOM SIGKILL at depth 1). Use the contents API to add pieces (recent naming: `YYYY-MM-DD-title.md`; numbered fiction prefixes go up to ~608).
- **tmux server was down** since the Sep 27 reboot (no socket). Check `tmux ls` before assuming sessions survive.
- **GitHub commit search text-matches commit messages** — a hit does NOT prove the sha is a git object (compare 404 = quoted text, not rot). See fleet-seeds scouts/2026-10-03-rd005-full-sweep.md.

## Fleet conventions (observed, receipted)

- Fleet repos commit straight to `main` for docs/scouts/lodes; PRs for code lanes.
- `gh repo list SuperInstance` caps at 1000; account is large.
- GitHub compare direction: `compare/{sha}...main` → status `ahead`/`identical` = sha IS ancestor of main.
