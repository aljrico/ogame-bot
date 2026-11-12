"""Entry point for OGame bot."""

import argparse
import os
from pathlib import Path

from src.ogame_bot.bot import OGameBot
from src.ogame_bot.config import OGameConfig
from src.ogame_bot.actions.fleet import Fleet
from src.ogame_bot.actions.navigation import Navigation
from src.ogame_bot.mission_config import load_expeditions
from src.ogame_bot.utils.delay import human_delay


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OGame bot.")
    parser.add_argument(
        "--expeditions-only",
        action="store_true",
        help=argparse.SUPPRESS,  # Deprecated no-op, kept so existing cron jobs don't break.
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

    _parse_args()

    config = OGameConfig.from_env()

    print(f"Lobby URL: {config.lobby_url}")
    print(f"Bot profile: {config.chrome_user_data_dir}\n")

    expeditions_path = _config_path("EXPEDITIONS_CONFIG", "expeditions.json")

    try:
        expedition_config = load_expeditions(expeditions_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Config error: {exc}")
        return

    print(f"Expeditions config: {expeditions_path}\n")

    with OGameBot(config) as bot:
        fleet = Fleet(bot.page)
        nav = Navigation(bot.page)

        print("\n" + "="*60)
        print("EXPEDITIONS")
        print("="*60)

        # Expedition slots are account-wide, so any planet works to read them.
        nav.select_planet(expedition_config.overflow_planet)
        nav.click_menu_by_text("Flota")

        available = fleet.get_available_expeditions()
        if expedition_config.max_expeditions is not None:
            available = min(available, expedition_config.max_expeditions)
        print(f"\n>>> {available} expedition slots available <<<\n")

        if available == 0:
            print("No expedition slots available, skipping expeditions.")
        else:
            # One expedition per listed planet (in priority order),
            # then any remaining slots from the overflow planet.
            origins = list(expedition_config.planets[:available])
            origins += [expedition_config.overflow_planet] * (available - len(origins))

            for i, planet in enumerate(origins):
                if i > 0:
                    # Randomized gap between expeditions so they aren't back-to-back.
                    human_delay(0.8, 1.8)
                print(f"\n--- Expedition {i + 1} of {available} (from {planet}) ---")
                fleet.send_expedition(
                    planet=planet,
                    ships=expedition_config.ships,
                )

        print("\n" + "="*60)
        print("ALL COMPLETE!")
        print("="*60)


if __name__ == "__main__":
    main()
