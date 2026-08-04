"""Unit tests for the crop-first Kaggriculture policy.

Official-game performance is tested by run_official_tournament.py.  These
tests only protect the local action priorities that caused the former agent to
buy inventory, harvest immature plants, and leave crops unwatered.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from agent import agent


def observation(tile, seeds=None, day=0, shed=None):
    return {
        "player": 0,
        "day": day,
        "hour": 0,
        "farms": [{
            "money": 3000,
            "tiles": [[tile]],
            "farmer": [0, 0],
            "hands": [],
            "unlocked_quadrants": ["NW"],
            "hires_today": 0,
        }],
        "private": {"seeds": seeds or {}, "shed": shed or {}},
    }


class CropFirstAgentTests(unittest.TestCase):
    def test_plants_available_seed_on_empty_tile(self):
        action = agent(observation(None, {"CARROT": 1}))
        self.assertEqual(action["farmer"], ["PLANT", "CARROT"])

    def test_waters_before_a_crop_is_ready(self):
        crop = {"kind": "PLANT", "crop": "CARROT", "planted_day": 0, "watered_today": False}
        action = agent(observation(crop, day=2))
        self.assertEqual(action["farmer"], ["WATER"])

    def test_harvests_carrot_only_at_best_yield_day(self):
        crop = {"kind": "PLANT", "crop": "CARROT", "planted_day": 0, "watered_today": True}
        action = agent(observation(crop, day=3))
        self.assertEqual(action["farmer"], ["HARVEST"])

    def test_sells_harvested_goods_without_buying_fertilizer(self):
        action = agent(observation(None, shed={"CARROT": 4}))
        self.assertIn(["SELL", "CARROT", 4], action["market"])
        self.assertNotIn(["BUY_PRODUCT", "FERTILIZER", 2], action["market"])


if __name__ == "__main__":
    unittest.main()
