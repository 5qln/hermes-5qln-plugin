#!/usr/bin/env python3
"""Tests for fractal_data_loop.py — stdlib unittest, no dependencies.

Run: python3 -m unittest test_fractal_loop -v   (from /opt/data/fractal-loop)
"""
import unittest

import fractal_data_loop as fl


class TestReduceExpand(unittest.TestCase):

    def test_empty_refused(self):
        seed, res = fl.reduce_data(b"", "witness", 5, 400)
        self.assertIsNone(seed)
        self.assertEqual(res["error"], "EMPTY_INPUT")

    def test_roundtrip_scales(self):
        for n in (1, 100, 5_000, 120_000, 1_000_000):
            data = (("scale test sentence %d. " % n) * (n // 22 + 1))[:n].encode()
            seed, res = fl.reduce_data(data, "witness", 5, 400)
            self.assertTrue(res["ok"])
            back, r2 = fl.expand_witness(seed)
            self.assertTrue(r2["ok"])
            self.assertEqual(back, data, "roundtrip failed at %d bytes" % n)

    def test_seed_bounded_any_size(self):
        for n in (256, 10_000, 2_000_000):
            data = b"x" * n
            seed, _ = fl.reduce_data(data, "witness", 5, 400)
            self.assertLessEqual(seed["n_leaves"], 400)

    def test_corruption_localized(self):
        data = b"corruption corpus. " * 400
        seed, _ = fl.reduce_data(data, "witness", 5, 400)
        bad = bytearray(data)
        bad[1234] ^= 0xFF
        v = fl.verify(seed, bytes(bad))
        self.assertFalse(v["ok"])
        self.assertEqual(v["level"], 0)
        self.assertEqual(v["node"], 1234 // seed["leaf_size"])

    def test_essence_verbatim(self):
        text = ("The loop reduces and expands. Every fragment is drawn verbatim. "
                "Nothing is generated from nothing. ") * 200
        seed, _ = fl.reduce_data(text.encode(), "essence", 5, 400)
        for level in seed["essence"]["levels"]:
            for frag in level:
                if not frag.startswith("0x"):
                    self.assertIn(frag, text)
        self.assertIn(seed["root_alpha"], text)

    def test_root_alpha_is_leaf_fragment(self):
        # parent's alpha is always one of its children's alphas, recursively:
        # the root fragment must exist verbatim in the source
        text = ("Alpha echo test. The same sentence repeats at every scale. "
                "Fractal identity holds. ") * 300
        seed, _ = fl.reduce_data(text.encode(), "essence", 5, 400)
        leaves = seed["essence"]["levels"][0]
        self.assertTrue(any(seed["root_alpha"] == f for f in leaves) or
                        seed["root_alpha"] in text)

    def test_determinism(self):
        data = b"determinism check " * 100
        s1, _ = fl.reduce_data(data, "both", 5, 400)
        s2, _ = fl.reduce_data(data, "both", 5, 400)
        self.assertEqual(s1["root_hash"], s2["root_hash"])

    def test_holographic_subtree(self):
        data = b"holographic node bytes. " * 2000
        seed, _ = fl.reduce_data(data, "witness", 5, 400)
        lv = seed["depth"] - 1
        sub, res = fl.expand_witness(seed, at=(lv, 2))
        self.assertTrue(res["ok"])
        self.assertIn(sub, data)

    def test_opaque_binary_honest(self):
        data = bytes(range(256)) * 200
        seed, _ = fl.reduce_data(data, "both", 5, 400)
        self.assertEqual(seed["alpha_kind"], "opaque")
        self.assertIsNone(seed["root_alpha"])

    def test_outline_grows_with_depth(self):
        text = ("Depth growth sentence one. Another distinct sentence here. "
                "A third unique line follows. ") * 300
        seed, _ = fl.reduce_data(text.encode(), "essence", 5, 400)
        o0, _ = fl.expand_essence(seed, depth=0)
        o2, _ = fl.expand_essence(seed, depth=2)
        self.assertGreater(len(o2.splitlines()), len(o0.splitlines()))

    def test_return_question_source_tagged(self):
        data = b"Source tagging matters. " * 100
        seed, _ = fl.reduce_data(data, "witness", 5, 400)
        self.assertEqual(seed["return_question_source"], "mechanical")
        seed2, _ = fl.reduce_data(data, "witness", 5, 400,
                                  return_question="What opens beyond this?")
        self.assertEqual(seed2["return_question_source"], "human")


if __name__ == "__main__":
    unittest.main()
