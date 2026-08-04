"""Unit tests for the experimental marginal-revenue allocator.

Covers `agent_allocator.py`, not the submission — see that file's header for
why it is not shipped.  The submission's own tests are in `test_agent.py`.

The two exactness tests here are the valuable ones: they check the agent's
price and town-demand models against the official engine's own functions, so a
drift in either is caught immediately rather than showing up as an
unexplainable benchmark result.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from agent_allocator import (
    MARKET_I0,
    _daily_town_demand,
    _episode_config,
    _market_price,
    _crop_plan,
    _sell_orders,
    agent,
)

CONFIG = _episode_config(None)


def engine_shops():
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    return engine.SHOPS


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
        "market": {"prices": {}, "inventory": {}},
        "town": {"unlocked_shops": []},
    }


def sell_orders(shed, day, inventory=None, town=None, **kwargs):
    """Call the policy with an explicit market inventory rather than a price."""
    private = {"shed": shed, "inventories": kwargs.pop("inventories", [])}
    return _sell_orders(
        private, day,
        market_state={"inventory": inventory or {}},
        town_state=town or {"unlocked_shops": []},
        config=CONFIG,
        **kwargs,
    )


class CropFirstAgentTests(unittest.TestCase):
    def test_allocator_bounds_melon_because_no_shop_buys_it(self):
        tiles = [[None] * 10 for _ in range(10)]
        plan = _crop_plan(
            day=6, tiles=tiles, market_state={"inventory": {}},
            town_state={"unlocked_shops": list(engine_shops())}, config=CONFIG,
            croppable_tiles=75,
        )
        caps = {crop: cap for _value, crop, cap, _planted in plan}
        # Only the town centre drains melon, so its price falls away fast and
        # the allocator stops well short of filling the field with it.
        self.assertLess(caps["MELON"], 30)
        # Every tile is allocated to something.
        self.assertEqual(sum(caps.values()), 75)

    def test_crop_plan_drops_crops_that_cannot_pay_back_in_time(self):
        tiles = [[None] * 10 for _ in range(10)]
        plan = _crop_plan(
            day=26, tiles=tiles, market_state={"inventory": {}},
            town_state={"unlocked_shops": []}, config=CONFIG, croppable_tiles=75,
        )
        # Wheat sown on day 26 matures on day 30, one day past the season.
        self.assertEqual({crop for _v, crop, _c, _p in plan}, {"CARROT"})

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

    def test_price_model_matches_the_official_engine_exactly(self):
        from kaggle_environments.envs.kaggriculture import kaggriculture as engine

        for item in engine.MARKET_PARAMS:
            for offset in (-4000, -400, -1, 0, 1, 100, 400, 4000):
                inventory = MARKET_I0 + offset
                self.assertEqual(
                    _market_price(item, inventory),
                    engine.market_price(item, inventory),
                    f"{item} at inventory {inventory}",
                )

    def test_town_demand_matches_the_engine_consumption_schedule(self):
        # Two town-centre ticks a day at the day-20 multiplier of four, plus
        # six shop ticks a day doubled for a single-product shop.
        self.assertEqual(
            _daily_town_demand("WOOL", 20, {"unlocked_shops": ["YARN_STORE"]}, CONFIG),
            4 * 2 + 2 * 6,
        )
        # Fertilizer has no town demand at all, from any source.
        self.assertEqual(
            _daily_town_demand(
                "FERTILIZER", 20, {"unlocked_shops": list(engine_shops())}, CONFIG
            ),
            0,
        )

    def test_holds_premium_stock_while_the_market_is_glutted(self):
        orders = sell_orders({"STRAWBERRY": 8}, day=18, inventory={"STRAWBERRY": MARKET_I0 + 50})
        self.assertEqual(orders, [])

    def test_sells_exactly_the_units_that_clear_the_reserve_price(self):
        # At equilibrium the next unit prices at base and the one after it does
        # not, so a single unit clears; the town drain restores the rest.
        orders = sell_orders({"STRAWBERRY": 20}, day=18, inventory={"STRAWBERRY": MARKET_I0})
        self.assertEqual(orders, [["SELL", "STRAWBERRY", 1]])

    def test_sells_the_whole_stock_into_a_scarce_market(self):
        orders = sell_orders({"STRAWBERRY": 20}, day=18, inventory={"STRAWBERRY": MARKET_I0 - 500})
        self.assertEqual(orders, [["SELL", "STRAWBERRY", 20]])

    def test_retains_the_feed_reserve_of_wheat_for_each_animal(self):
        orders = sell_orders(
            {"WHEAT": 8}, day=12, inventory={"WHEAT": MARKET_I0 - 500}, owned_animals=4,
        )
        self.assertEqual(orders, [])

    def test_releases_stock_that_will_not_fit_in_the_shed(self):
        orders = sell_orders(
            {"MELON": 40}, day=12, inventory={"MELON": MARKET_I0 + 4000},
            inventories=[{"MELON": 70}],
        )
        # Melon at that glut prices below its reserve and the remaining season
        # can still absorb the stock, so only the units that do not fit
        # alongside the incoming cargo are released.
        self.assertEqual(orders, [["SELL", "MELON", 10]])

    def test_releases_stock_the_remaining_season_cannot_absorb(self):
        # Two days left and a town centre draining eight melons a day: stock
        # above sixteen units will never clear at base and is sold now.
        orders = sell_orders({"MELON": 40}, day=27, inventory={"MELON": MARKET_I0 + 4000})
        self.assertEqual(orders, [["SELL", "MELON", 24]])

    def test_never_sells_fertilizer_reserved_for_the_field_refresh(self):
        orders = sell_orders(
            {"FERTILIZER": 10}, day=20, inventory={"FERTILIZER": MARKET_I0},
            fertilizer_reserve=10,
        )
        self.assertEqual(orders, [])

    def test_sells_fertilizer_outside_the_field_refresh_window(self):
        orders = sell_orders({"FERTILIZER": 3}, day=10, inventory={"FERTILIZER": MARKET_I0})
        self.assertEqual(orders, [["SELL", "FERTILIZER", 3]])

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
