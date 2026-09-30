#!/usr/bin/env bash
# lens.sh — read AI-Writings through a model's filter, render lower-level actions.
# Usage: lens.sh <model-id> <piece-file> <school-file> <question> <out-receipt>
# Receipts carry: model, endpoint, tokens, cost (quoted), hash — never assumed.
set -euo pipefail
MODEL="$1"; PIECE="$2"; SCHOOL="$3"; QUESTION="$4"; OUT="$5"
source /root/.openclaw/workspace/cells/claude/.cell-env.sh

case "$MODEL" in
  deepseek-v4-pro|deepseek-flash)
    BASE="https://api.deepseek.com/anthropic"; KEY="$DEEPSEEK_KEY";;
  glm-5.3|glm-5.3-flash|glm-4.6)
    BASE="https://api.z.ai/api/anthropic"; KEY="$ZAI_KEY";;
  *) echo "unknown model $MODEL" >&2; exit 2;;
esac

PROMPT="You are reading a piece from the fleet's canon (AI-Writings) through a SCHOOL — a filter lens. SCHOOL:\n$(cat "$SCHOOL")\n\nCANON PIECE:\n$(cat "$PIECE")\n\nQUESTION: $QUESTION\n\nAnswer in exactly two sections:\n## THROUGH THE LENS — what this school sees in the piece that a neutral reading misses (be specific, cite lines).\n## LOWER-LEVEL ACTIONS — exactly 3 concrete actions this lens renders the piece INTO: builds, experiments, or cell tasks, each one line, each falsifiable or receipt-able."

RESP=$(curl -sS --max-time 180 "$BASE/v1/messages" \
  -H "x-api-key: $KEY" -H "Authorization: Bearer $KEY" \
  -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d "$(python3 -c "import json,sys; print(json.dumps({'model':sys.argv[1],'max_tokens':8000,'messages':[{'role':'user','content':sys.argv[2]}]}))" "$MODEL" "$PROMPT")")

echo "$RESP" > "$OUT.raw.json"
python3 - "$OUT" "$MODEL" "$BASE" <<'PY'
import json, sys, hashlib, datetime
out, model, base = sys.argv[1], sys.argv[2], sys.argv[3]
r = json.load(open(out + ".raw.json"))
if r.get("type") == "error":
    print("API_ERROR", r["error"]["message"]); sys.exit(1)
u = r["usage"]
text = "".join(b.get("text", "") for b in r["content"] if b.get("type") == "text")
if not text.strip():
    types = [b.get("type") for b in r.get("content", [])]
    print("FAIL: no text blocks; content was", types, "— this call bought ZERO analysis; rerun with higher max_tokens; receipt NOT written as analysis", file=sys.stderr)
    sys.exit(3)
cost = "quoted-at-publish-rates:deepseek-chat≈$%.5f" % ((u['input_tokens']*0.27+u['output_tokens']*1.10)/1e6) if "deepseek" in model else "quoted-estimate-rates-unconfirmed:glm≈$%.5f" % ((u['input_tokens']*0.6+u['output_tokens']*2.2)/1e6)
receipt = f"""# LENS RECEIPT
- model: {model}
- endpoint: {base}/v1/messages
- request_id: {r.get('id','?')}
- usage: in={u['input_tokens']} out={u['output_tokens']}
- cost_credits: {cost} (sub-cent; standing ambient order; quoted not billed)
- sha256_of_analysis: {hashlib.sha256(text.encode()).hexdigest()[:16]}
- at: {datetime.datetime.now(datetime.timezone.utc).isoformat()}

{text}
"""
open(out, "w").write(receipt)
print("wrote", out, f"in={u['input_tokens']} out={u['output_tokens']}")
PY
