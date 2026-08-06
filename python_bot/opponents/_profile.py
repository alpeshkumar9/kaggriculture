"""Load isolated replay-derived variants of the frozen W10 opponent."""

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def build_replay_agent(episode_id):
    directory = Path(__file__).resolve().parent
    profiles = json.loads((directory / "profiles.json").read_text(encoding="utf-8"))
    profile = profiles[str(episode_id)]
    source = directory.parent / "opponent_base.py"
    spec = spec_from_file_location(f"_replay_{episode_id}_base", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen opponent base: {source}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, value in profile["settings"].items():
        if name == "LAND_PLAN":
            value = tuple(tuple(entry) for entry in value)
        setattr(module, name, value)
    return module.agent
