"""Configuration management for OGame bot."""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot's own profile directory (separate from your main Chrome)
BOT_PROFILE_DIR = Path.home() / ".ogame-bot" / "chrome-profile"


@dataclass
class OGameConfig:
    """OGame bot configuration."""

    chrome_user_data_dir: str
    language: str = "es_ES"
    headless: bool = False
    slow_mo: int = 50  # ms delay between actions

    @classmethod
    def from_env(cls) -> "OGameConfig":
        """Load configuration from environment variables."""
        # Use bot's dedicated profile by default
        profile_dir = os.getenv("CHROME_USER_DATA_DIR", str(BOT_PROFILE_DIR))

        # Ensure profile directory exists
        Path(profile_dir).mkdir(parents=True, exist_ok=True)

        return cls(
            chrome_user_data_dir=profile_dir,
            language=os.getenv("OGAME_LANGUAGE", "es_ES"),
            headless=os.getenv("HEADLESS", "false").lower() == "true",
            slow_mo=int(os.getenv("SLOW_MO", "50")),
        )

    @property
    def lobby_url(self) -> str:
        """Get lobby URL for configured language."""
        return f"https://lobby.ogame.gameforge.com/{self.language}/hub"

    @property
    def is_first_run(self) -> bool:
        """Check if this is the first run (no saved session)."""
        profile_path = Path(self.chrome_user_data_dir)
        # Check for cookies/login data
        return not (profile_path / "Default" / "Cookies").exists()
