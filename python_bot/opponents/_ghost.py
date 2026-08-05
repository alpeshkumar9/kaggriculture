"""Replay a real opponent's submitted action sequence on its source seed."""

import copy
import json
from pathlib import Path


def build_ghost_agent(episode_id):
    source = Path(__file__).resolve().parent / "ghost_actions.json"
    actions = json.loads(source.read_text(encoding="utf-8"))[str(episode_id)]

    def agent(observation, configuration=None):
        obs = observation if isinstance(observation, dict) else getattr(observation, "__dict__", {})
        turns_per_day = 24
        if isinstance(configuration, dict):
            turns_per_day = int(configuration.get("turnsPerDay", turns_per_day))
        elif configuration is not None:
            turns_per_day = int(getattr(configuration, "turnsPerDay", turns_per_day))
        step = int(obs.get("step", int(obs.get("day", 0)) * turns_per_day + int(obs.get("hour", 0))))
        # Kaggle replay step N stores the action that produced observation N.
        # At observation N the agent must therefore issue the recorded action
        # from N+1.
        action_index = step + 1
        if 0 <= action_index < len(actions):
            return copy.deepcopy(actions[action_index])
        return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent
