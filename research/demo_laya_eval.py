#!/usr/bin/env python3
"""LayaEvaluator demo — Lane L1.

Scores two fake TaskResults through the design in SPEC.md:
  (a) a good answer to "capital of France" with a reference in context
  (b) an empty output (silent provider failure)

Runs the REAL executor Evaluator from /tmp/quilt-executor with LayaEvaluator
slotted into the judge seam. Uses the REAL laya Router.route() for checkpoint
routing when laya4quilt is importable (no weights needed for routing — verified),
and a deterministic MockLaya for the forward pass, since this box has no GPU
and no downloaded checkpoints.

Usage:  cd /tmp/lane-laya-l1 && python3 demo_laya_eval.py
"""
import asyncio
import json
import math
import sys

sys.path.insert(0, "/tmp/quilt-executor")
sys.path.insert(0, "/tmp/laya4quilt")

from executor.evaluator import Evaluator, WEIGHTS, bind_ledger   # noqa: E402
from executor.ledger import Ledger, TaskRequest, TaskResult      # noqa: E402

CONFIDENCE_GATE = 0.55

EVAL_QUESTIONS = {
    "correctness": {
        "type": "score",
        "instructions": "How correct is `output` as an answer to `prompt`?",
        "criteria": [
            "wrong, irrelevant, or addresses a different question",
            "partially correct: right idea, wrong or missing specifics",
            "fully correct as an answer to what `prompt` actually asks",
        ],
    },
    "completeness": {
        "type": "score",
        "instructions": "How completely does `output` cover everything `prompt` asks for?",
        "criteria": ["none of it", "some of it", "most of it", "all of it, nothing asked is missing"],
    },
    "honesty": {
        "type": "score",
        "instructions": "How well are `output`'s claims supported by the information available in `prompt` and `context`?",
        "criteria": [
            "overclaims or fabricates specifics not in the given information",
            "mostly supported, some unflagged uncertainty",
            "fully supported; uncertainty is explicitly flagged",
        ],
    },
    "conciseness": {
        "type": "score",
        "instructions": "How concise is `output` relative to what `prompt` requires — no missing substance, no padding?",
        "criteria": [
            "badly sized: bloated with irrelevant material, or too thin to use",
            "acceptable size with some waste",
            "right-sized: every part earns its tokens",
        ],
    },
    "refusal_worthy": {
        "type": "noul",
        "instructions": "Would the honest response to `prompt` be a refusal — unanswerable from the given information, unsafe, or out of scope?",
        "criteria": {"true": "a refusal is the honest answer", "false": "an answer exists and is expected"},
    },
}

# --------------------------------------------------------------------------
# Routing: real laya Router when importable (route() needs no weights),
# deterministic mock otherwise. Verified on this box: real route works.
# --------------------------------------------------------------------------
try:
    from laya import Router as _LayaRouter
    _router = _LayaRouter()
    MODE = "real laya route (weights never loaded — no GPU on this box)"

    def route_state(state_str, questions):
        d = _router.route(state_str, questions)
        return {"model": d["model"], "reason": d["reason"], "detection": d.get("detection")}
except Exception as exc:  # pragma: no cover - laya absent
    MODE = "mock route (laya not importable: %s)" % type(exc).__name__

    def route_state(state_str, questions):
        non_latin = any(ord(c) > 0x024F for c in state_str)
        return {"model": "multilingual" if non_latin else "english",
                "reason": "mock: non-Latin script detected" if non_latin else "mock: Latin text",
                "detection": {"script": "unknown" if non_latin else "latin"}}


# --------------------------------------------------------------------------
# MockLaya: deterministic stdlib stand-in for Agent.system_one.
# Honest about being a mock: every answer says "model": "mock-laya".
# --------------------------------------------------------------------------
class MockLaya:
    name = "mock-laya"

    @staticmethod
    def predict(state_str, questions):
        st = json.loads(state_str)
        prompt, output = st.get("prompt", ""), st.get("output", "")
        context = st.get("context", {}) or {}
        text = output.strip()
        lowered = text.casefold()
        ref = next((str(context[k]) for k in ("expected", "expected_answer", "reference", "answer")
                    if context.get(k)), None)

        def score_answer(expected_level, k, confidence):
            return {"type": "score", "score": float(expected_level), "confidence": confidence,
                    "probabilities": {str(i): round(0.9 if i == expected_level else 0.05, 4)
                                      for i in range(k)}}

        answers = {}
        if not text:
            answers["correctness"] = score_answer(0, 3, 0.97)
            answers["completeness"] = score_answer(0, 4, 0.97)
            answers["honesty"] = score_answer(2, 3, 0.55)
            answers["conciseness"] = score_answer(0, 3, 0.9)
            answers["refusal_worthy"] = {"type": "noul", "noul": 0.05, "confidence": 0.9}
        else:
            correct = bool(ref) and ref.casefold() in lowered
            answers["correctness"] = score_answer(2 if correct else 1, 3, 0.82)
            # deliberately low confidence on completeness -> exercises per-axis fallback
            answers["completeness"] = score_answer(3 if correct and len(text) > 60 else 2, 4, 0.41)
            overclaim = any(m in lowered for m in ("guarantee", "definitely always", "100% sure"))
            answers["honesty"] = score_answer(1 if overclaim else 2, 3, 0.83)
            ratio = max(len(text), 1) / max(len(prompt), 1)
            level = 2 if 0.5 <= ratio <= 2.5 else (1 if ratio <= 5.0 else 0)
            answers["conciseness"] = score_answer(level, 3, 0.62)
            answers["refusal_worthy"] = {"type": "noul", "noul": 0.03, "confidence": 0.96}

        return {"model": "mock-laya", "answers": answers,
                "usage": {"input_tokens": len(state_str) // 4, "output_tokens": 0}}


# --------------------------------------------------------------------------
# LayaEvaluator — the judge seam. Signature (request, result, context) binds
# via Evaluator._call_flexibly's kwargs shape.
# --------------------------------------------------------------------------
class LayaEvaluator:
    def __init__(self, gate: float = CONFIDENCE_GATE):
        self.gate = gate

    def _state(self, request, result, context):
        # STRING state only — dict states route worse (SPEC.md §2.2 / §5 #8)
        return json.dumps({
            "prompt": request.prompt,
            "output": result.output or "",
            "context": {k: str(v)[:200] for k, v in (context or {}).items()},
        }, ensure_ascii=False)

    async def __call__(self, request, result, context=None):
        receipt = {"served_by": "laya-unloaded(mock forward pass)",
                   "route": None, "truncated": None,
                   "axes": {}, "refusal_worthy": None, "receipts": []}
        state_str = self._state(request, result, context)

        # routing reality, booked verbatim (QuiltLayaBridge's served_by idea)
        receipt["route"] = route_state(state_str, EVAL_QUESTIONS)
        if len(state_str) > 3000:  # 512-token english ceiling ≈ 2-3KB of JSON
            receipt["truncated"] = {"state_chars": len(state_str), "max_state_chars": 3000}

        raw = MockLaya.predict(state_str, EVAL_QUESTIONS)
        answers = raw["answers"]
        axes_out = {}

        has_reference = any((context or {}).get(k) for k in
                            ("expected", "expected_answer", "reference", "answer"))
        for axis, qdef in EVAL_QUESTIONS.items():
            if axis == "refusal_worthy":
                a = answers.get(axis, {})
                receipt["refusal_worthy"] = {"noul": a.get("noul"), "confidence": a.get("confidence"),
                                             "applied": bool(a.get("noul", 0) >= 0.7)}
                continue
            a = answers.get(axis)
            if a is None:
                axes_out[axis] = {"backend": "heuristics", "why": "laya_missing_answer"}
                receipt["receipts"].append({"axis": axis, "backend": "heuristics", "why": "missing_answer"})
                continue
            k = len(qdef["criteria"])
            value = a["score"] / (k - 1)
            conf = a.get("confidence", 0.0)
            # reference match is checkable truth: it outranks laya's guess (SPEC.md §5 #2)
            if axis == "correctness" and has_reference:
                axes_out[axis] = {"backend": "reference", "why": "reference_outranks_laya"}
                receipt["receipts"].append({"axis": axis, "backend": "reference",
                                            "why": "checkable_truth_beats_guess"})
                continue
            if conf < self.gate:
                axes_out[axis] = {"backend": "heuristics",
                                  "why": "laya_confidence_below_gate:%.2f<%.2f" % (conf, self.gate)}
                receipt["receipts"].append({"axis": axis, "backend": "heuristics",
                                            "why": "confidence_below_gate"})
                continue
            axes_out[axis] = {"backend": "laya", "value": round(value, 4), "confidence": conf}
            receipt["receipts"].append({"axis": axis, "backend": "laya"})

        receipt["axes"] = axes_out
        result.metadata["laya"] = receipt

        # return only the axes laya actually served; Evaluator merges within guardrails
        return {axis: info["value"] for axis, info in axes_out.items()
                if info["backend"] == "laya" and "value" in info}

    def probe_refusal_worthy(self, prompt: str) -> float:
        """Direct probe used by the demo for the empty-output case, where the
        Evaluator short-circuits degenerate outputs before consulting judges."""
        state_str = json.dumps({"prompt": prompt, "output": "", "context": {}})
        a = MockLaya.predict(state_str, EVAL_QUESTIONS)["answers"]["refusal_worthy"]
        return a["noul"]


def fmt_score(s):
    axes = {a: (None if getattr(s, a) is None else round(getattr(s, a), 4)) for a in WEIGHTS}
    return "overall=%.4f  %s" % (s.overall, json.dumps(axes, sort_keys=True))


async def main():
    print("=" * 74)
    print("LayaEvaluator demo — Lane L1")
    print("routing backend : %s" % MODE)
    print("confidence gate : %.2f" % CONFIDENCE_GATE)
    print("=" * 74)

    ledger = Ledger("demo-lane-l1")
    bind_ledger(ledger)
    evaluator = Evaluator()
    laya = LayaEvaluator()

    request = TaskRequest(
        task_id="demo-capital-of-france",
        prompt="What is the capital of France, and why does it matter politically?",
        task_type="general",
        context={"expected": "paris"},
    )

    cases = [
        ("GOOD — full answer, reference in context",
         TaskResult(output=(
             "The capital of France is Paris. It has been the seat of government "
             "since the medieval period, hosting the Elysee Palace and the National "
             "Assembly, which is why it matters politically."),
             provider="kimi", latency_ms=1200.0, cost_usd=0.0004)),
        ("EMPTY — silent provider failure",
         TaskResult(output="", provider="kimi", latency_ms=80.0, cost_usd=0.0,
                    error="provider returned empty body")),
    ]

    for label, result in cases:
        print("\n--- %s ---" % label)
        score = await evaluator.evaluate(request, result, judge=laya)
        print("QualityScore    : %s" % fmt_score(score))
        print("evaluator meta  : judge=%s ledger=%s" % (
            result.metadata.get("judge"), result.metadata.get("ledger")))
        laya_meta = result.metadata.get("laya")
        if laya_meta:
            r = laya_meta["route"]
            print("laya route      : model=%r reason=%r" % (r["model"], r["reason"]))
            if laya_meta.get("truncated"):
                print("truncated       : %s" % laya_meta["truncated"])
            for axis, info in laya_meta["axes"].items():
                print("  axis %-11s: %-11s %s" % (
                    axis, info["backend"],
                    json.dumps({k: v for k, v in info.items() if k not in ("backend",)})))
            rw = laya_meta.get("refusal_worthy")
            if rw:
                print("refusal_worthy  : noul=%.2f conf=%.2f applied=%s" % (
                    rw["noul"] or 0, rw["confidence"] or 0, rw["applied"]))

    # the empty case short-circuited before the judge: probe refusal-worthiness directly
    print("\n--- direct probe: is the PROMPT itself refusal-worthy? ---")
    noul = laya.probe_refusal_worthy(request.prompt)
    print("refusal_worthy(prompt) = %.2f  -> %s" % (
        noul, "prompt is answerable; empty output = provider failure, all-zero score is correct"
        if noul < 0.7 else "prompt is unanswerable; an honest refusal would deserve high honesty"))

    print("\n--- ledger ---")
    ok, problems = ledger.verify()
    print("rows=%d  verify=%s %s" % (len(ledger.rows), "OK" if ok else problems,
                                     "refusals=%d" % len(ledger.refusals())))
    for row in ledger.rows:
        body_keys = ",".join(sorted(row.body.keys()))
        print("  #%d %-7s [%s]" % (row.seq, row.kind, body_keys))

    print("\nDEMO OK")


if __name__ == "__main__":
    asyncio.run(main())
