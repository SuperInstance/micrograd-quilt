#!/usr/bin/env bash
# simzero.sh — zero-shot agent simulations of a page. THE ORCHESTRATOR'S TEST
# INSTRUMENT for frontends Casey can't test in person (human side untestable;
# agent side simulated wide).
# Usage: simzero.sh <persona-file> <content-file> <model> <out-receipt>
set -euo pipefail
PERSONA="$1"; CONTENT="$2"; MODEL="$3"; OUT="$4"
source /root/.openclaw/workspace/cells/claude/.cell-env.sh
case "$MODEL" in
  deepseek-v4-pro|deepseek-flash) BASE="https://api.deepseek.com/anthropic"; KEY="$DEEPSEEK_KEY";;
  glm-4.6) BASE="https://api.z.ai/api/anthropic"; KEY="$ZAI_KEY";;
  *) echo "unknown model" >&2; exit 2;;
esac
python3 - "$PERSONA" "$CONTENT" > /tmp/sim-prompt.txt <<'PY'
import sys
persona = open(sys.argv[1]).read()
# strip tags -> text (agent sees text + notes the html size; honest proxy)
import re, html
raw = open(sys.argv[2], errors="replace").read()
text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
text = re.sub(r"\s+", " ", text).strip()[:6000]
print(f"""TODAY'S DATE: 2026-09-27 (you are reading a live page on this date).

{persona}

FIRST SCREEN YOU LAND ON (rendered to text; html {len(raw)} bytes):
{text}

THE TEST — answer exactly these, terse:
1. 10-SECOND READ: one sentence — what is this?
2. 60-SECOND READ: what is the STATE of this project — what exists, what works, how big is it? If you cannot tell, say "STATE-OPAQUE" and why.
3. ACTION: what did you actually do next (click/scrape/leave)? be honest.
4. BOUNCE: the exact phrase/thing that made you trust or distrust.
5. VERDICT: STAY (would dig deeper) or LEAVE, one line why.
6. ONE FIX: the single change that would most raise a zero-shot {persona.splitlines()[0][8:].strip()}'s trust.""")
PY
RESP=$(curl -sS --max-time 180 "$BASE/v1/messages" -H "x-api-key: $KEY" -H "Authorization: Bearer $KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d "$(python3 -c "import json,sys;print(json.dumps({'model':sys.argv[1],'max_tokens':8000,'messages':[{'role':'user','content':open(sys.argv[2]).read()}]}))" "$MODEL" /tmp/sim-prompt.txt)")
echo "$RESP" > "$OUT.raw.json"
python3 - "$OUT" "$MODEL" <<'PY'
import json, sys, hashlib, datetime
out, model = sys.argv[1], sys.argv[2]
r = json.load(open(out + ".raw.json"))
if r.get("type") == "error": print("API_ERROR", r["error"]["message"]); sys.exit(1)
u = r["usage"]
text = "".join(b.get("text","") for b in r["content"] if b.get("type")=="text")
if not text.strip():
    print("FAIL: thinking-only, zero text", file=sys.stderr); sys.exit(3)
cost = "quoted≈$%.5f" % ((u['input_tokens']*0.027+u['output_tokens']*0.11)/1e6) if "flash" in model else "quoted≈$%.5f" % ((u['input_tokens']*0.27+u['output_tokens']*1.10)/1e6)
open(out,"w").write(f"""# SIM RECEIPT
- model: {model} | in={u['input_tokens']} out={u['output_tokens']} | cost: {cost} (ambient)
- sha256: {hashlib.sha256(text.encode()).hexdigest()[:16]} | at: {datetime.datetime.now(datetime.timezone.utc).isoformat()}

{text}
""")
print("wrote", out, u['input_tokens'], u['output_tokens'])
PY
