"""Load mission configuration from JSON files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExpeditionConfig:
    planet: str
    ships: dict[str, int]
    max_expeditions: int | None = None


@dataclass(frozen=True)
class FarmingConfig:
    planet: str
    ships: dict[str, int]
    targets: list[tuple[int, int, int]]


def load_expeditions(path: Path) -> ExpeditionConfig:
    data = _load_json(path)
    planet = _require_str(data, "planet", path)
    ships = _require_ships(data, path)
    max_expeditions = data.get("max_expeditions")
    if max_expeditions is not None:
        if not isinstance(max_expeditions, int) or max_expeditions < 0:
            raise ValueError(f"{path}: max_expeditions must be a non-negative integer")
    return ExpeditionConfig(planet=planet, ships=ships, max_expeditions=max_expeditions)


def load_farming(path: Path) -> FarmingConfig:
    data = _load_json(path)
    planet = _require_str(data, "planet", path)
    ships = _require_ships(data, path)
    targets = _require_targets(data, path)
    return FarmingConfig(planet=planet, ships=ships, targets=targets)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object at the root")
    return data


def _require_str(data: dict[str, Any], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: '{key}' must be a non-empty string")
    return value


def _require_ships(data: dict[str, Any], path: Path) -> dict[str, int]:
    ships = data.get("ships")
    if not isinstance(ships, dict) or not ships:
        raise ValueError(f"{path}: 'ships' must be a non-empty object")
    parsed: dict[str, int] = {}
    for name, count in ships.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{path}: ship names must be non-empty strings")
        if not isinstance(count, int) or count <= 0:
            raise ValueError(f"{path}: ship counts must be positive integers")
        parsed[name] = count
    return parsed


def _require_targets(data: dict[str, Any], path: Path) -> list[tuple[int, int, int]]:
    targets = data.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError(f"{path}: 'targets' must be a non-empty array")
    parsed: list[tuple[int, int, int]] = []
    for target in targets:
        if not isinstance(target, (list, tuple)) or len(target) != 3:
            raise ValueError(f"{path}: targets must be [galaxy, system, position] triples")
        galaxy, system, position = target
        if not all(isinstance(value, int) and value > 0 for value in (galaxy, system, position)):
            raise ValueError(f"{path}: target coordinates must be positive integers")
        parsed.append((galaxy, system, position))
    return parsed
