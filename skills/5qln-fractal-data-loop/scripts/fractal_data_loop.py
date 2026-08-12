#!/usr/bin/env python3
"""
fractal_data_loop.py — the 5QLN fractal data operator.

Reduce any-size data to a bounded seed; expand the seed back out, fractally.
Every node of the tree is itself a complete seed (XY := X within Y).

Two honest modes:

  WITNESS  (lossless)  — seed carries zlib cargo + a 5-ary fractal hash spine.
                         expand() regenerates the exact bytes and re-verifies
                         the identity (≡) at every level. Any corruption is
                         reported with its level and node path. Honest failure.

  ESSENCE  (lossy)     — seed carries only a bounded tree of extractive
                         fragments: every node's alpha is drawn VERBATIM from
                         its own subtree, and a parent's alpha is always one of
                         its children's alphas — so the root fragment exists
                         word-for-word in the leaves. expand(depth=d) unfolds a
                         fractal outline at 5^d granularity. It never claims
                         to be the original.

Phase mapping (the loop IS the grammar, not a metaphor):
  REDUCE  = G iterated:  alpha ≡ {alpha'} at every scale until one root.
  EXPAND  = V iterated:  each level re-crystallizes and is checked ≡ its seed.
  Q per node: a node commits to ALL its children or fails closed (no L4 node).
  P: adaptive leaf size — the spine stays bounded for ANY input size; maximum
     granularity value per unit of seed.
  S / ∞0': the seed carries a return question, source-tagged. Empty input is
     refused — no seed is manufactured from nothing.

This instrument is standalone (not part of the hermes-5qln-plugin runtime).
Standard library only. Deterministic: same input -> same seed.

Self-negation: this seed is a pointer, not the data itself.
"""

import argparse
import base64
import hashlib
import json
import math
import os
import re
import sys
import zlib

FORMAT = "5qln-fractal-seed/1"
CODEX_PIN = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"
LEAF_PREFIX = b"5QLN/LEAF/1"
NODE_PREFIX = b"5QLN/NODE/1"
SELF_NEGATION = (
    "This seed is a pointer, not the data itself. Essence expansion "
    "regenerates a faithful outline built of verbatim fragments; it never "
    "reproduces the original."
)
MIN_LEAF = 256
ALPHA_CAP = 200  # max chars per stored fragment


# --------------------------------------------------------------------------
# primitives

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def leaf_hash(chunk: bytes) -> str:
    return sha256(LEAF_PREFIX + chunk)


def node_hash(child_hashes) -> str:
    return sha256(NODE_PREFIX + b"".join(bytes.fromhex(h) for h in child_hashes))


def choose_leaf_size(n_bytes: int, arity: int, budget: int) -> int:
    """Adaptive leaf size: keep total node count <= budget for ANY input size.

    A 5-ary tree over L leaves holds ~ L * arity/(arity-1) nodes total.
    This is the P-phase of the operator: maximum granularity per unit seed.
    """
    target_leaves = max(1, budget * (arity - 1) // arity)
    raw = max(MIN_LEAF, math.ceil(n_bytes / target_leaves))
    return int(math.ceil(raw / MIN_LEAF)) * MIN_LEAF


def build_tree(data: bytes, leaf_size: int, arity: int):
    """Return levels[0..depth]; levels[0] = leaf hashes, levels[-1] = [root]."""
    leaves = [data[i:i + leaf_size] for i in range(0, len(data), leaf_size)] or [b""]
    levels = [[leaf_hash(c) for c in leaves]]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        parent = [node_hash(cur[i:i + arity]) for i in range(0, len(cur), arity)]
        levels.append(parent)
    return levels, len(leaves)


# --------------------------------------------------------------------------
# essence extraction (deterministic, extractive — never generative)

WORD_RE = re.compile(r"[a-z0-9]{3,}")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def decode_text(data: bytes):
    """Return (text, opaque_flag). Opaque = not honestly readable as text."""
    text = data.decode("utf-8", errors="replace")
    if not text.strip():
        return text, True
    replaced = text.count("\ufffd")
    if replaced / max(1, len(text)) > 0.01:
        return text, True
    return text, False


def fragments(text: str):
    """Candidate verbatim fragments: sentences (long ones -> verbatim window)."""
    out = []
    for s in SENT_SPLIT.split(text):
        s = s.strip()
        if len(s) < 24:
            continue
        out.append(s[:ALPHA_CAP])
    return out


def tf_table(text: str):
    tf = {}
    for w in WORD_RE.findall(text.lower()):
        tf[w] = tf.get(w, 0) + 1
    return tf


def score(fragment: str, tf) -> float:
    words = WORD_RE.findall(fragment.lower())
    if not words:
        return 0.0
    return sum(tf.get(w, 0) for w in words) / math.sqrt(len(words))


def best_fragment(text: str):
    """The most central verbatim fragment of text, or None if opaque."""
    cands = fragments(text)
    if not cands:
        return None
    tf = tf_table(text)
    return max(cands, key=lambda f: (score(f, tf), -text.find(f)))


def essence_alphas(data: bytes, levels, leaf_size: int, arity: int):
    """alpha per node, every level. A parent's alpha is exactly one of its
    children's alphas, so every ancestor's words exist verbatim in a leaf."""
    text, opaque = decode_text(data)
    if opaque:
        return None, "opaque"
    # leaf alphas
    chunks = [data[i:i + leaf_size] for i in range(0, len(data), leaf_size)]
    level_a = []
    for c in chunks:
        t, op = decode_text(c)
        level_a.append(None if op else best_fragment(t))
    if not any(level_a):
        return None, "opaque"
    alphas = [level_a]
    # parents inherit the strongest child alpha (scored among siblings)
    while len(alphas[-1]) > 1:
        cur = alphas[-1]
        parent = []
        for i in range(0, len(cur), arity):
            sibs = [a for a in cur[i:i + arity] if a]
            if not sibs:
                parent.append(None)
                continue
            tf = tf_table(" . ".join(sibs))
            parent.append(max(sibs, key=lambda f: (score(f, tf), -len(f))))
        alphas.append(parent)
    # root fallback
    if not alphas[-1][0]:
        alphas[-1][0] = best_fragment(text)
    return alphas, "text"


# --------------------------------------------------------------------------
# reduce

def reduce_data(data: bytes, mode: str, arity: int, budget: int,
                return_question=None):
    if not data:
        # L2 guard: no seed is manufactured from nothing.
        return None, {
            "ok": False,
            "error": "EMPTY_INPUT",
            "detail": "No seed from empty input. S is not manufactured from K.",
        }
    leaf_size = choose_leaf_size(len(data), arity, budget)
    levels, n_leaves = build_tree(data, leaf_size, arity)
    depth = len(levels) - 1

    alphas, alpha_kind = (None, "n/a")
    if mode in ("essence", "both"):
        alphas, alpha_kind = essence_alphas(data, levels, leaf_size, arity)
    elif mode == "witness":
        # still try a root fragment for the seed card; honest if opaque
        text, opaque = decode_text(data)
        if not opaque:
            a, k = essence_alphas(data, levels, leaf_size, arity)
            if a:
                alphas, alpha_kind = ([[None]] * depth + [a[-1]]), k
            else:
                alpha_kind = "opaque"

    root_alpha = None
    if alphas:
        root_alpha = alphas[-1][0]

    if return_question:
        rq, rq_src = return_question, "human"
    elif root_alpha:
        rq = "What does the whole say that this fragment only begins to say: \"%s\"?" \
             % root_alpha[:80]
        rq_src = "mechanical"
    else:
        rq = "What is this opaque corpus the record of?"
        rq_src = "mechanical"

    seed = {
        "format": FORMAT,
        "codex_pin": CODEX_PIN,
        "mode": mode,
        "arity": arity,
        "leaf_size": leaf_size,
        "original_size": len(data),
        "n_leaves": n_leaves,
        "depth": depth,
        "root_hash": levels[-1][0],
        "alpha_kind": alpha_kind,
        "root_alpha": root_alpha,
        "return_question": rq,
        "return_question_source": rq_src,
        "self_negation": SELF_NEGATION,
        "spine": {"levels": levels},
    }
    if mode in ("witness", "both"):
        cargo = zlib.compress(data, 9)
        seed["cargo_b64_z"] = base64.b64encode(cargo).decode("ascii")
        seed["compression_ratio"] = round(len(cargo) / len(data), 4)
    if mode in ("essence", "both") and alphas:
        seed["essence"] = {
            "levels": [
                [a if a else "0x" + h[:16] for a, h in zip(alphas[i], levels[i])]
                for i in range(len(alphas))
            ]
        }
    return seed, {"ok": True}


# --------------------------------------------------------------------------
# expand

def expand_witness(seed, at=None):
    """Regenerate exact bytes; verify ≡ at every level. Honest failure."""
    try:
        data = zlib.decompress(base64.b64decode(seed["cargo_b64_z"]))
    except Exception as e:
        return None, {"ok": False, "error": "CARGO_CORRUPT", "detail": str(e)}
    levels, _ = build_tree(data, seed["leaf_size"], seed["arity"])
    stored = seed["spine"]["levels"]
    for lv in range(len(stored)):
        want = stored[lv]
        got = levels[lv] if lv < len(levels) else []
        if len(want) != len(got):
            return None, {"ok": False, "error": "FRACTURE",
                          "level": lv, "detail": "node count drifted"}
        for i, (w, g) in enumerate(zip(want, got)):
            if w != g:
                return None, {"ok": False, "error": "FRACTURE",
                              "level": lv, "node": i,
                              "detail": "identity broken at L%d:%d" % (lv, i)}
    if at:
        lv, idx = at
        per_leaf = seed["leaf_size"]
        span = seed["arity"] ** (seed["depth"] - lv)
        start_leaf = idx * span
        end_leaf = min(start_leaf + span, seed["n_leaves"])
        chunk = data[start_leaf * per_leaf:end_leaf * per_leaf]
        return chunk, {"ok": True, "verified": "all-levels",
                       "subtree": "L%d:%d" % (lv, idx)}
    return data, {"ok": True, "verified": "all-levels"}


def expand_essence(seed, depth=None, at=None):
    """Unfold the alpha-tree as a fractal outline. Never claims the original."""
    ess = seed.get("essence")
    if not ess:
        return None, {"ok": False, "error": "NO_ESSENCE",
                      "detail": "seed carries no essence tree"}
    levels = ess["levels"]           # levels[0]=leaves ... levels[-1]=[root]
    top = len(levels) - 1
    show = top if depth is None else min(depth, top)
    lines = []

    def walk(lv, idx, indent):
        frag = levels[lv][idx] if 0 <= lv < len(levels) and idx < len(levels[lv]) else "?"
        lines.append("%s- %s" % ("  " * indent, frag))
        if indent >= show or lv == 0:
            return
        arity = seed["arity"]
        # children of node (lv, idx) sit one level down at idx*arity .. idx*arity+arity-1
        for ci in range(idx * arity, min(idx * arity + arity, len(levels[lv - 1]))):
            walk(lv - 1, ci, indent + 1)

    if at:
        lv, idx = at
        walk(lv, idx, 0)
    else:
        walk(top, 0, 0)
    outline = "\n".join(lines)
    return outline, {"ok": True, "depth_shown": show, "note": SELF_NEGATION}


# --------------------------------------------------------------------------
# verify / card

def verify(seed, data: bytes):
    levels, _ = build_tree(data, seed["leaf_size"], seed["arity"])
    stored = seed["spine"]["levels"]
    if levels[-1][0] == stored[-1][0]:
        return {"ok": True, "result": "≡ HOLDS", "root": stored[-1][0]}
    for lv in range(min(len(stored), len(levels))):
        for i, (w, g) in enumerate(zip(stored[lv], levels[lv])):
            if w != g:
                return {"ok": False, "result": "≡ BROKEN",
                        "level": lv, "node": i}
    return {"ok": False, "result": "≡ BROKEN", "detail": "shape drift"}


def seed_card(seed):
    js = json.dumps(seed)
    lines = [
        "5QLN FRACTAL SEED — card",
        "  format        %s" % seed["format"],
        "  codex pin     %s…" % seed["codex_pin"][:16],
        "  mode          %s" % seed["mode"],
        "  arity         %d (holographic: every node is a complete seed)" % seed["arity"],
        "  original      %d bytes" % seed["original_size"],
        "  leaves        %d × %d bytes" % (seed["n_leaves"], seed["leaf_size"]),
        "  depth         %d" % seed["depth"],
        "  seed size     %d bytes (json)" % len(js.encode()),
    ]
    if "compression_ratio" in seed:
        lines.append("  compression   %.3f (cargo/original)" % seed["compression_ratio"])
    lines += [
        "  root ≡        %s…" % seed["root_hash"][:32],
        "  alpha kind    %s" % seed["alpha_kind"],
    ]
    if seed.get("root_alpha"):
        lines.append("  root alpha    \"%s\"" % seed["root_alpha"][:120])
    lines += [
        "  ∞0'           %s" % seed["return_question"],
        "  ∞0' source    %s" % seed["return_question_source"],
        "  self-negation %s" % seed["self_negation"][:72] + "…",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# self-test — falsifiable, honest report

def self_test():
    out = []

    def check(name, cond, detail=""):
        out.append({"test": name, "pass": bool(cond), "detail": detail})
        return cond

    # 1. empty input refused
    seed, res = reduce_data(b"", "witness", 5, 400)
    check("empty input refused (L2 guard)", seed is None and res["error"] == "EMPTY_INPUT")

    # 2. roundtrip across scales
    sizes = [1, 100, 5000, 120000, 2_000_000]
    for n in sizes:
        data = (("the quick brown fox jumps over the lazy dog %d. " % n) *
                (n // 45 + 1))[:n].encode()
        seed, res = reduce_data(data, "witness", 5, 400)
        back, r2 = expand_witness(seed)
        check("witness roundtrip %d bytes" % n, back == data,
              "depth=%d ratio=%.3f" % (seed["depth"], seed["compression_ratio"]))
        check("seed bounded for %d bytes" % n,
              seed["n_leaves"] <= 400, "leaves=%d" % seed["n_leaves"])

    # 3. corruption localized honestly
    data = b"corruption test corpus. " * 500
    seed, _ = reduce_data(data, "witness", 5, 400)
    bad = bytearray(data)
    bad[7000] ^= 0xFF
    v = verify(seed, bytes(bad))
    check("corruption localized", (not v["ok"]) and v.get("level") == 0,
          json.dumps(v))

    # 4. essence fragments verbatim
    text = ("5QLN begins from not knowing. The seed carries the whole. "
            "Every scale echoes the same essence. Fracture is reported honestly. "
            "The loop returns a question. ") * 300
    seed, _ = reduce_data(text.encode(), "essence", 5, 400)
    verbatim = all(
        (frag.startswith("0x") or frag in text)
        for level in seed["essence"]["levels"] for frag in level
    )
    check("every essence fragment verbatim", verbatim)
    check("root alpha verbatim", seed["root_alpha"] in text, seed["root_alpha"][:60])

    # 5. determinism
    s1, _ = reduce_data(text.encode(), "essence", 5, 400)
    s2, _ = reduce_data(text.encode(), "essence", 5, 400)
    check("deterministic", s1["root_hash"] == s2["root_hash"])

    # 6. holographic subtree expansion
    seed, _ = reduce_data(data, "witness", 5, 400)
    sub, r = expand_witness(seed, at=(max(0, seed["depth"] - 1), 1 if seed["n_leaves"] > 5 else 0))
    check("holographic subtree expands", r["ok"] and sub and sub in data)

    # 7. essence outline grows fractally
    seed, _ = reduce_data(text.encode(), "essence", 5, 400)
    o0, _ = expand_essence(seed, depth=0)
    o2, _ = expand_essence(seed, depth=2)
    check("outline granularity grows with depth",
          len(o2.splitlines()) > len(o0.splitlines()),
          "d0=%d lines d2=%d lines" % (len(o0.splitlines()), len(o2.splitlines())))

    passed = sum(1 for o in out if o["pass"])
    return {"passed": passed, "total": len(out), "tests": out,
            "ok": passed == len(out)}


# --------------------------------------------------------------------------
# CLI

def _read_input(path):
    if path == "-":
        return sys.stdin.buffer.read()
    with open(path, "rb") as f:
        return f.read()


def _parse_at(s):
    m = re.match(r"^(\d+):(\d+)$", s or "")
    if not m:
        raise SystemExit("--at must be 'L:i' (level:node)")
    return int(m.group(1)), int(m.group(2))


def main(argv=None):
    p = argparse.ArgumentParser(description="5QLN fractal loop — reduce/expand any data")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reduce", help="data -> seed")
    r.add_argument("input", help="file path, or - for stdin")
    r.add_argument("--mode", choices=["witness", "essence", "both"], default="both")
    r.add_argument("--arity", type=int, default=5)
    r.add_argument("--budget", type=int, default=400,
                   help="max tree nodes; seed spine stays bounded for any input")
    r.add_argument("--return-question", default=None,
                   help="human-supplied ∞0' (else a mechanical one, labeled as such)")
    r.add_argument("-o", "--out", default=None)

    e = sub.add_parser("expand", help="seed -> data (witness) or outline (essence)")
    e.add_argument("seed")
    e.add_argument("--depth", type=int, default=None, help="essence outline depth")
    e.add_argument("--at", default=None, help="expand subtree L:i (holographic)")
    e.add_argument("-o", "--out", default=None)

    v = sub.add_parser("verify", help="≡ test: does this file decompress from this seed?")
    v.add_argument("seed")
    v.add_argument("input")

    c = sub.add_parser("seed", help="print the seed card")
    c.add_argument("seed")

    sub.add_parser("self-test", help="run the falsifiable suite")

    args = p.parse_args(argv)

    if args.cmd == "reduce":
        data = _read_input(args.input)
        seed, res = reduce_data(data, args.mode, args.arity, args.budget,
                                args.return_question)
        if not res["ok"]:
            print(json.dumps(res, indent=2))
            return 1
        payload = json.dumps(seed, indent=2, ensure_ascii=False)
        if args.out:
            with open(args.out, "w") as f:
                f.write(payload)
            print(seed_card(seed))
            print("\n[seed written to %s]" % args.out)
        else:
            print(payload)
        return 0

    if args.cmd == "expand":
        with open(args.seed) as f:
            seed = json.load(f)
        at = _parse_at(args.at) if args.at else None
        if "cargo_b64_z" in seed and args.depth is None and args.out != "-":
            out, res = expand_witness(seed, at=at)
            if not res["ok"]:
                print(json.dumps(res, indent=2))
                return 1
            if args.out:
                with open(args.out, "wb") as f:
                    f.write(out)
                print(json.dumps({"ok": True, "verified": res["verified"],
                                  "bytes": len(out), "out": args.out}, indent=2))
            else:
                sys.stdout.buffer.write(out)
            return 0
        out, res = expand_essence(seed, depth=args.depth, at=at)
        if not res["ok"]:
            print(json.dumps(res, indent=2))
            return 1
        text = out + "\n\n[" + res["note"] + "]"
        if args.out and args.out != "-":
            with open(args.out, "w") as f:
                f.write(text)
        else:
            print(text)
        return 0

    if args.cmd == "verify":
        with open(args.seed) as f:
            seed = json.load(f)
        data = _read_input(args.input)
        res = verify(seed, data)
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1

    if args.cmd == "seed":
        with open(args.seed) as f:
            seed = json.load(f)
        print(seed_card(seed))
        return 0

    if args.cmd == "self-test":
        rep = self_test()
        print(json.dumps(rep, indent=2))
        return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
