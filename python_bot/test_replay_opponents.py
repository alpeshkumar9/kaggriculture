"""Tests for replay-derived opponent generation and tournament routing."""

import json
import sys
import unittest
from pathlib import Path


BOT_DIR = Path(__file__).resolve().parent
OPPONENT_DIR = BOT_DIR / "opponents"
sys.path.insert(0, str(BOT_DIR))
sys.path.insert(0, str(OPPONENT_DIR))

from opponents._ghost import build_ghost_agent  # noqa: E402
from run_official_tournament import replay_roster_entries, resolve_opponent  # noqa: E402


class ReplayOpponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        from build_replay_opponents import ensure_opponents_synced
        ensure_opponents_synced()
        cls.profiles = json.loads(
            (OPPONENT_DIR / "profiles.json").read_text(encoding="utf-8")
        )


    def test_every_full_log_has_one_replay_opponent(self):
        full_logs = {
            path.stem for path in (BOT_DIR.parent / "logs").glob("**/*.json")
            if "-" not in path.stem
        }
        self.assertEqual(set(self.profiles), full_logs)
        self.assertEqual(len(replay_roster_entries()), len(full_logs))

    def test_known_player_seat_is_excluded(self):
        self.assertEqual(self.profiles["89980458"]["source_name"], "vlad101")
        self.assertEqual(self.profiles["89980458"]["source_seat"], 0)

    def test_missing_player_identity_uses_documented_fallback(self):
        profile = self.profiles["90006347"]
        self.assertEqual(profile["source_name"], "somewhere after")
        self.assertIn("higher-scoring seat", profile["selection"])

    def test_ghost_uses_action_that_produces_the_next_observation(self):
        actions = json.loads(
            (OPPONENT_DIR / "ghost_actions.json").read_text(encoding="utf-8")
        )["89978502"]
        ghost = build_ghost_agent("89978502")
        self.assertEqual(ghost({"step": 0}), actions[1])

    def test_weak_builtin_name_is_not_resolved(self):
        with self.assertRaises(ValueError):
            resolve_opponent("unsupported-builtin", lambda observation, configuration=None: {})

    def test_dynamic_opponent_resolution(self):
        # Resolve a dummy/virtual path that doesn't exist on disk
        ghost_path = str(OPPONENT_DIR / "replay_89978502.py")
        # Ensure we delete the generated file if it existed
        if Path(ghost_path).exists():
            Path(ghost_path).unlink()
        
        agent_fn = resolve_opponent(ghost_path, lambda observation, configuration=None: {})
        self.assertTrue(callable(agent_fn))



if __name__ == "__main__":
    unittest.main()
