#!/usr/bin/env bash
# fresh-audit-pr.sh — run a repo's pins in a PRISTINE clone before opening/trusting a PR.
#
# Doctrine (R85 wound class, phantom-RED detector): a green run in the author's
# dirty tree proves nothing — uncommitted files, inherited CWD, and local state
# can make pins pass (or fail) for reasons the merge target will never see.
# This wrapper is the review-loop adoption: canonical tool is quilt-tools
# PR #45 (fresh-audit v0); until that merges this script implements the same
# minimal law standalone so the loop can adopt the discipline NOW.
#
# Usage:
#   scripts/fresh-audit-pr.sh run <repo-path-or-url> <branch> <pin-cmd> [pin-cmd-args...]
#   scripts/fresh-audit-pr.sh selftest
#
# Law enforced:
#   1. pins run inside a fresh clone of the branch, never the caller's tree
#   2. CWD is anchored to the clone root (the #45 P2 bug class: inheriting the
#      caller's CWD and reading the author's files by relative path)
#   3. exit status propagates: phantom-RED must stay RED, not be laundered

set -euo pipefail

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
mode="${1:-}"

_FA_TMP=""  # global so the EXIT trap can see it past function scope (set -u law)
cleanup() { [ -n "$_FA_TMP" ] && rm -rf "$_FA_TMP"; }
trap cleanup EXIT

fail() { echo "fresh-audit: FAIL: $*" >&2; exit 1; }

run_pristine() {
  local repo="$1" branch="$2"; shift 2
  [ $# -ge 1 ] || fail "run: pin command required"
  command -v git >/dev/null || fail "git not found"

  local tmp
  tmp="$(mktemp -d /tmp/fresh-audit.XXXXXX)"
  _FA_TMP="$tmp"

  git clone --quiet --depth 1 --branch "$branch" "$repo" "$tmp/clone" \
    || fail "clone of '$repo' @ '$branch' failed (branch exists?)"
  # CWD anchor: every relative path in the pin command resolves inside the
  # clone, never against the author's working tree.
  cd "$tmp/clone"
  echo "fresh-audit: pristine clone at $(pwd)"
  echo "fresh-audit: pins: $*"
  if "$@"; then
    echo "fresh-audit: PASS (pins green in pristine clone of $branch)"
  else
    local rc=$?
    echo "fresh-audit: RED (pins failed in pristine clone with exit $rc — phantom-RED class if they pass in your tree)" >&2
    exit "$rc"
  fi
}

selftest() {
  local tmp pass=0
  tmp="$(mktemp -d /tmp/fresh-audit-selftest.XXXXXX)"
  _FA_TMP="$tmp"

  mkrepo() { # mkrepo <name> <pin-script-content>
    mkdir -p "$tmp/$1"
    ( cd "$tmp/$1" && git init -q . && printf '%s\n' "$2" > pin.sh \
      && git add pin.sh && git -c user.email=t@t -c user.name=t commit -qm pin )
  }

  # T1: RED propagation — pin fails in pristine clone → runner exits nonzero
  mkrepo red 'echo fake-pin; exit 1'
  if "$SELF" run "$tmp/red" master bash pin.sh >/dev/null 2>&1; then
    fail "selftest T1: failing pin did not propagate RED"
  fi
  pass=$((pass+1)); echo "selftest T1 ok: phantom-RED stays RED (nonzero exit)"

  # T2: CWD anchoring — pin asserts CWD is the clone root, not the caller's
  mkrepo cwdanchor 'test "$PWD" = "$(git rev-parse --show-toplevel)" || { echo "CWD leak: $PWD"; exit 1; }'
  ( cd "$tmp" && "$SELF" run "$tmp/cwdanchor" master bash pin.sh >/dev/null 2>&1 ) \
    || fail "selftest T2: pin inherited caller CWD instead of clone root"
  pass=$((pass+1)); echo "selftest T2 ok: CWD anchored to clone root even when invoked elsewhere"

  # T3: author's dirty tree is invisible — uncommitted helper file in the
  # source repo must NOT be visible to the pin
  mkdir -p "$tmp/dirty" && ( cd "$tmp/dirty" && git init -q . \
    && echo 'test ! -f helper.txt' > pin.sh && echo "uncommitted-helper" > helper.txt \
    && git add pin.sh && git -c user.email=t@t -c user.name=t commit -qm pin )
  "$SELF" run "$tmp/dirty" master bash pin.sh >/dev/null 2>&1 \
    || fail "selftest T3: pristine clone saw the author's uncommitted files"
  pass=$((pass+1)); echo "selftest T3 ok: uncommitted author-tree files invisible in pristine clone"

  echo "selftest: $pass/3 green"
}

case "$mode" in
  run) shift; run_pristine "$@" ;;
  selftest) selftest ;;
  *) grep '^#' "$0" | head -8; exit 2 ;;
esac
