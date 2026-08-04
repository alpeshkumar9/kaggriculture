"""Unit tests for the crop-first Kaggriculture policy.

Official-game performance is tested by run_official_tournament.py.  These
tests only protect the local action priorities that caused the former agent to
buy inventory, harvest immature plants, and leave crops unwatered.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from agent import agent, _sell_orders


def observation(tile, seeds=None, day=0, shed=None, hires_today=0):
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
            "hires_today": hires_today,
        }],
        "private": {"seeds": seeds or {}, "shed": shed or {}},
        "market": {"prices": {}},
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
        obs = observation(None, shed={"CARROT": 4}, hires_today=10)
        obs["market"]["prices"]["CARROT"] = 35
        action = agent(obs)
        self.assertIn(["SELL", "CARROT", 4], action["market"])
        self.assertNotIn(["BUY_PRODUCT", "FERTILIZER", 2], action["market"])

    def test_holds_low_price_premium_stock_when_shed_has_room(self):
        orders = _sell_orders(
            {"shed": {"STRAWBERRY": 8}}, day=18,
            market_state={"prices": {"STRAWBERRY": 1}},
        )
        self.assertEqual(orders, [])

    def test_sells_a_bounded_premium_tranche_after_price_recovers(self):
        orders = _sell_orders(
            {"shed": {"STRAWBERRY": 20}}, day=18,
            market_state={"prices": {"STRAWBERRY": 120}},
        )
        self.assertEqual(orders, [["SELL", "STRAWBERRY", 8]])

    def test_retains_three_feed_days_of_wheat_for_each_cow(self):
        orders = _sell_orders(
            {"shed": {"WHEAT": 12}}, day=12,
            market_state={"prices": {"WHEAT": 40}}, owned_cows=4,
        )
        self.assertEqual(orders, [])

    def test_tomato_is_watered_and_harvested_as_an_ongoing_crop(self):
        tomato = {
            "kind": "PLANT", "crop": "TOMATO", "planted_day": 4,
            "watered_today": False, "consecutive_unwatered": 1,
        }
        self.assertEqual(agent(observation(tomato, day=11))["farmer"], ["WATER"])
        tomato["watered_today"] = True
        tomato["yield_units"] = 1
        self.assertEqual(agent(observation(tomato, day=11))["farmer"], ["HARVEST"])


if __name__ == "__main__":
    unittest.main()
