#!/usr/bin/env python3
"""Tests for axis_stasis.py — the 5QLN axis stasis detector.

Run:  python3 test_axis_stasis.py          (from this directory)
or:   python3 -m unittest test_axis_stasis

Stdlib only.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from axis_stasis import detect_stasis, axis_signature  # noqa: E402


def mk(alpha, scope, sha="sha-%d", corruption=0, ts=None, n=0):
    """Build one synthetic trail reading."""
    return {
        "timestamp": ts or "2026-08-%02dT00:00:00+00:00" % (5 + n),
        "cycles": 80 + n,
        "alpha_direction": alpha,
        "inf0p_scope": scope,
        "corruption_total": corruption,
        "liveness_avg": 5.0,
        "signature_sha": sha % n if "%" in str(sha) else sha,
    }


class TestAxisSignature(unittest.TestCase):
    def test_known_pair(self):
        self.assertEqual(axis_signature(mk("outward", "narrowing")),
                         ("outward", "narrowing"))

    def test_unknown_alpha(self):
        self.assertIsNone(axis_signature(mk("unknown", "narrowing")))

    def test_missing_scope(self):
        r = mk("outward", "narrowing")
        del r["inf0p_scope"]
        self.assertIsNone(axis_signature(r))


class TestDetectStasis(unittest.TestCase):
    def test_stasis_fires(self):
        rs = [mk("outward", "narrowing", n=i) for i in range(3)]
        r = detect_stasis(rs, k=3)
        self.assertEqual(r["verdict"], "STASIS")
        self.assertEqual(r["axis"], ["outward", "narrowing"])
        self.assertEqual(len(r["window"]), 3)

    def test_moving_axis_does_not_fire(self):
        rs = [mk("outward", "narrowing", n=0),
              mk("outward", "narrowing", n=1),
              mk("inward", "widening", n=2)]
        self.assertEqual(detect_stasis(rs, k=3)["verdict"], "MOVING")

    def test_k_default_is_three(self):
        rs = [mk("outward", "narrowing", n=i) for i in range(3)]
        self.assertEqual(detect_stasis(rs)["verdict"], "STASIS")

    def test_short_trail_insufficient(self):
        rs = [mk("outward", "narrowing", n=i) for i in range(2)]
        r = detect_stasis(rs, k=3)
        self.assertEqual(r["verdict"], "INSUFFICIENT_DATA")

    def test_unknown_axis_in_window_insufficient(self):
        rs = [mk("outward", "narrowing", n=0),
              mk("unknown", "narrowing", n=1),
              mk("outward", "narrowing", n=2)]
        self.assertEqual(detect_stasis(rs, k=3)["verdict"], "INSUFFICIENT_DATA")

    def test_still_when_content_does_not_move(self):
        rs = [mk("outward", "narrowing", sha="same", n=0),
              mk("outward", "narrowing", sha="same", n=1),
              mk("outward", "narrowing", sha="same", n=2)]
        r = detect_stasis(rs, k=3)
        self.assertEqual(r["verdict"], "STILL")
        self.assertFalse(r["content_moved"])

    def test_corruption_does_not_block_stasis(self):
        # Corruption is the watcher's lane; the stasis detector reads the axis only.
        rs = [mk("outward", "narrowing", corruption=2, n=i) for i in range(3)]
        self.assertEqual(detect_stasis(rs, k=3)["verdict"], "STASIS")

    def test_k_equals_two(self):
        rs = [mk("outward", "narrowing", n=0),
              mk("outward", "narrowing", n=1)]
        self.assertEqual(detect_stasis(rs, k=2)["verdict"], "STASIS")

    def test_k_below_two_rejected(self):
        with self.assertRaises(ValueError):
            detect_stasis([mk("outward", "narrowing")], k=1)

    def test_empty_trail(self):
        self.assertEqual(detect_stasis([], k=3)["verdict"], "INSUFFICIENT_DATA")


if __name__ == "__main__":
    unittest.main()
