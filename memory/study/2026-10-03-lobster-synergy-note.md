# lobster synergy note — GitHub-native agent shape (snowball pulse 15:11)

Date: 2026-10-03 15:11 Asia/Shanghai. Source: SuperInstance/lobster (created
03:38Z, pushed 03:47Z). Read directly: README.md, ONBOARDING.md, TASKS.md,
VAULT.md, .github/workflows/think.yml, and the permission head of
.github/scripts/agent.py. Status: SYNERGY CANDIDATE / ADOPT-VOCABULARY, no
collision. lobster is a GitHub-native OpenClaw-shaped agent: repo is body,
commits are work/memory, issues/PRs are board/comms, scheduled ReAct loop via
OIDC-vault, dangerous actions deferred rather than blocked, `git_push_main`
explicitly deferred, human reviews via git log.

Adoption map for this lane: (1) snowball queue + receipts are already
time-shaped memory, but this pulse found prior receipt lines still dirty — the
lobster law to adopt is stricter: every receipt/state change gets committed in
the same pulse or named as uncommitted debt; (2) its markdown task board plus
GitHub issues duality matches our queue-file plus PR-issue workflow — keep both,
but make the queue file the digest and git log the truth; (3) its defer-not-block
permission shape is the same doctrine as our branch+commit/never-push-main rule,
useful vocabulary for future tool permissions; (4) vault/OIDC key handling is
org infrastructure, not this lane's build target.

Honest boundary: lobster is a hosting/organism experiment, not a queue-item
replacement; no code change here beyond this note. Rivalry risk: low — it
presumes GitHub Actions + vault; our lane remains workstation/OpenClaw-native.
