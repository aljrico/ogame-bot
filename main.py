"""Entry point for OGame bot."""

import argparse
import os
from pathlib import Path

from src.ogame_bot.bot import OGameBot
from src.ogame_bot.config import OGameConfig
from src.ogame_bot.actions.fleet import Fleet
from src.ogame_bot.actions.navigation import Navigation
from src.ogame_bot.mission_config import load_expeditions, load_farming


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OGame bot.")
    parser.add_argument(
        "--expeditions-only",
        action="store_true",
        help="Run only expedition missions and skip farming.",
    )
    return parser.parse_args()


def _config_path(env_key: str, default_name: str) -> Path:
    raw_path = os.getenv(env_key)
    if raw_path:
        return Path(raw_path).expanduser()
    return Path(__file__).resolve().parent / "config" / default_name


def main():
    """Run the OGame bot."""
    print("Starting OGame Bot...\n")

    args = _parse_args()

    config = OGameConfig.from_env()

    print(f"Lobby URL: {config.lobby_url}")
    print(f"Bot profile: {config.chrome_user_data_dir}\n")

    expeditions_path = _config_path("EXPEDITIONS_CONFIG", "expeditions.json")
    farming_path = _config_path("FARMING_CONFIG", "farming.json")

    try:
        expedition_config = load_expeditions(expeditions_path)
        farming_config = None
        if not args.expeditions_only:
            farming_config = load_farming(farming_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Config error: {exc}")
        return

    print(f"Expeditions config: {expeditions_path}")
    if not args.expeditions_only:
        print(f"Farming config: {farming_path}")
    print()

    with OGameBot(config) as bot:
        fleet = Fleet(bot.page)
        nav = Navigation(bot.page)

        # === 1. EXPEDITIONS ===
        print("\n" + "="*60)
        print("PHASE 1: EXPEDITIONS")
        print("="*60)

        nav.select_planet(expedition_config.planet)
        nav.click_menu_by_text("Flota")

        available = fleet.get_available_expeditions()
        if expedition_config.max_expeditions is not None:
            available = min(available, expedition_config.max_expeditions)
        print(f"\n>>> {available} expedition slots available <<<\n")

        if available == 0:
            print("No expedition slots available, skipping expeditions.")
        else:
            for i in range(available):
                print(f"\n--- Expedition {i + 1} of {available} ---")
                fleet.send_expedition(
                    planet=expedition_config.planet,
                    ships=expedition_config.ships,
                )

        # === 2. FARM ATTACKS ===
        if args.expeditions_only:
            print("\n" + "="*60)
            print("PHASE 2: FARM ATTACKS (SKIPPED)")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("PHASE 2: FARM ATTACKS")
            print("="*60)

            fleet.send_farm_attacks(
                planet=farming_config.planet,
                ships=farming_config.ships,
                targets=farming_config.targets,
            )

        print("\n" + "="*60)
        print("ALL COMPLETE!")
        print("="*60)


if __name__ == "__main__":
    main()
