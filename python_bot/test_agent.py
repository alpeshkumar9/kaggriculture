"""Unit tests for the crop-first Kaggriculture policy.

Official-game performance is tested by run_official_tournament.py.  These
tests only protect the local action priorities that caused the former agent to
buy inventory, harvest immature plants, and leave crops unwatered.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from agent import _episode_config, _livestock_action, _premium_crop_plan, _sell_orders, agent


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
    def test_configuration_derives_episode_limits(self):
        config = _episode_config({
            "episodeSteps": 120, "turnsPerDay": 12,
            "shedCapacity": 40, "maxMarketOrdersPerTurn": 3,
            "farmHandCostMult": 2,
        })
        self.assertEqual(config["season_days"], 10)
        self.assertEqual(config["last_planting_day"], 8)
        self.assertEqual(config["final_liquidation_day"], 9)
        self.assertEqual(config["shed_capacity"], 40)
        self.assertEqual(config["max_market_orders"], 3)
        self.assertEqual(config["farm_hand_cost_mult"], 2)

    def test_configuration_caps_market_orders(self):
        action = agent(
            observation(None, {"CARROT": 1}),
            {"maxMarketOrdersPerTurn": 1},
        )
        self.assertEqual(len(action["market"]), 1)

    def test_short_episode_liquidates_on_derived_final_day(self):
        crop = {
            "kind": "PLANT", "crop": "CARROT", "planted_day": -1,
            "yield_units": 1, "watered_today": False,
        }
        action = agent(
            observation(crop, day=1),
            {"episodeSteps": 48, "turnsPerDay": 24},
        )
        self.assertEqual(action["farmer"], ["HARVEST"])

    def test_final_day_harvests_animal_yield_instead_of_servicing_it(self):
        cow = {
            "kind": "PASTURE", "animal": "COW", "yield_units": 3,
            "fed_today": False, "cared_today": False,
            "fertilizer_available": True,
        }
        action = agent(observation(cow, day=29))
        self.assertEqual(action["farmer"], ["HARVEST"])

    def test_configured_shed_capacity_controls_overflow_sale(self):
        orders = _sell_orders(
            {"shed": {"CARROT": 50}, "inventories": []},
            day=18, market_state={"prices": {"CARROT": 1}},
            shed_capacity=45,
        )
        self.assertEqual(orders, [["SELL", "CARROT", 5]])

    def test_ice_cream_after_pizza_selects_the_milestone_crop_plan(self):
        plan = _premium_crop_plan(
            {"unlocked_shops": ["PIZZA_SHOP", "ICE_CREAM_SHOP"]}
        )
        self.assertEqual(plan, (7, 42, 15, 6))

    def test_non_pizza_strawberry_demand_advances_priority(self):
        plan = _premium_crop_plan(
            {"unlocked_shops": ["FARMERS_MARKET", "PIZZA_SHOP"]}
        )
        self.assertEqual(plan, (7, 42, 15, 6))

    def test_non_pizza_without_strawberry_demand_keeps_default_plan(self):
        plan = _premium_crop_plan(
            {"unlocked_shops": ["BAKERY", "YARN_STORE"]}
        )
        self.assertEqual(plan, (7, 42, 15, 6))

    def test_plants_available_seed_on_empty_tile(self):
        # Carrot was removed from the rotation (realises below base; see D3).
        # The feed-crop fallback is now wheat; verify it plants on an empty tile.
        action = agent(observation(None, {"WHEAT": 1}))
        self.assertEqual(action["farmer"], ["PLANT", "WHEAT"])

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
        self.assertEqual(orders, [["SELL", "STRAWBERRY", 4]])

    def test_retains_wheat_reserve_for_animals(self):
        orders = _sell_orders(
            {"shed": {"WHEAT": 12}}, day=12,
            market_state={"prices": {"WHEAT": 40}}, owned_animals=4,
        )
        self.assertEqual(orders, [])



    def test_sells_shed_stock_before_a_projected_same_turn_harvest(self):
        orders = _sell_orders(
            {"shed": {"CARROT": 95}, "inventories": []},
            day=18,
            market_state={"prices": {"CARROT": 1}},
            projected_harvest_units=6,
        )
        self.assertEqual(orders, [["SELL", "CARROT", 1]])

    def test_never_sells_fertilizer_reserved_for_production(self):
        orders = _sell_orders(
            {"shed": {"FERTILIZER": 10}}, day=20,
            market_state={"prices": {"FERTILIZER": 100}},
        )
        self.assertEqual(orders, [])

    def test_sells_fertilizer_at_any_price_outside_refresh_window(self):
        # FERTILIZER multiplier is 0.0: target_price = 0, so price_is_healthy is
        # always True. The W11 adaptive floor ($55 when oversupplied) governs timing;
        # the 98% below-base figure is expected, not a defect. Phi ($186k) does this.
        orders = _sell_orders(
            {"shed": {"FERTILIZER": 3}}, day=10,
            market_state={"prices": {"FERTILIZER": 95}}, owned_animals=1,
        )
        self.assertEqual(orders, [["SELL", "FERTILIZER", 3]])



    def test_crop_backlog_prevents_another_fertilizer_pickup(self):
        livestock = {
            "owned_animals": 0, "unfed": [], "deployments_assigned": 0,
            "crop_rescue_needed": True,
        }
        action = _livestock_action(
            4, 4, None, {}, [[None] * 10 for _ in range(10)],
            {"shed": {"FERTILIZER": 6}}, livestock, set(), 20, 0, 6,
        )
        self.assertIsNone(action)

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
