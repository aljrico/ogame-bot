"""Main OGame bot class."""

from playwright.sync_api import Page

from .config import OGameConfig
from .browser import BrowserManager
from .login import LoginHandler, LoginError


class OGameBot:
    """Main bot orchestrator."""

    def __init__(self, config: OGameConfig | None = None):
        self.config = config or OGameConfig.from_env()
        self.browser_manager = BrowserManager(self.config)
        self._game_page: Page | None = None

    def __enter__(self) -> "OGameBot":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        """Start the bot - launch browser and login."""
        if self.config.is_first_run:
            print("First run detected! You'll need to log in with Google once.")
            print("Your session will be saved for future runs.\n")

        print(f"Opening Chrome and navigating to {self.config.lobby_url}...")

        self.browser_manager.start()
        lobby_page = self.browser_manager.goto_lobby()

        login_handler = LoginHandler(lobby_page, self.browser_manager.context)

        try:
            # Try automatic login (just clicking Play buttons)
            self._game_page = login_handler.login()
        except LoginError as e:
            print(f"\nAutomatic login failed: {e}")
            # Fall back to manual login
            self._game_page = login_handler.wait_for_manual_login()

        print("Bot ready!")

    @property
    def page(self) -> Page:
        """Get the game page."""
        if self._game_page:
            return self._game_page
        raise RuntimeError("Bot not started")

    def stop(self):
        """Stop the bot."""
        self.browser_manager.stop()

    # === Actions (to be implemented) ===

    def get_resources(self) -> dict:
        """Get current resource levels."""
        # TODO: Parse resource bar
        raise NotImplementedError("Resource parsing not yet implemented")

    def build(self, building: str):
        """Queue a building upgrade."""
        # TODO: Navigate to building and click upgrade
        raise NotImplementedError("Building not yet implemented")

    def research(self, tech: str):
        """Queue a research."""
        # TODO: Navigate to research and click
        raise NotImplementedError("Research not yet implemented")

    def fleetsave(self):
        """Send fleet on expedition to protect from raids."""
        # TODO: Implement fleetsave
        raise NotImplementedError("Fleetsave not yet implemented")
