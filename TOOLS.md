# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## Hard rules (earned 2026-09-24, two near-catastrophic cwd incidents)

1. **Never run `git` without `-C /abs/path`.** No exceptions, no "I'll cd first."
   cwd resets between exec calls — silently, every time you assume otherwise.
2. **Never `git add -A` outside a freshly-verified repo.** Explicit paths only.
   Rule 2 saved the workspace twice on 09-24: the accidental commit of 11 embedded
   repos went nowhere because `git add executor/providers.py` didn't match.
3. **Before any push: `git remote -v | head -1` must name the intended repo.**
   The workspace repo's origin is micrograd-quilt; a wrong-cwd push polluted
   org main and needed a public revert (9700319 + 383e36c — the honest kind, not force-push).
4. **Never force-push org mains.** Revert, don't rewrite. Public history stays.
5. For python test runs from other repos: `cd /abs && python3 -m unittest discover -s tests -q`
   as a STANDALONE command — chaining is where the cd gets dropped.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
