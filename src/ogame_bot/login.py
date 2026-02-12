"""Login functionality for OGame."""

from playwright.sync_api import Page, BrowserContext, TimeoutError as PlaywrightTimeout


class LoginError(Exception):
    """Raised when automatic login fails."""
    pass


class LoginHandler:
    """Handles OGame authentication flow using existing Google login."""

    # Selectors
    LOBBY_PLAY_BUTTON = "button:has-text('Jugar')"
    GAME_PLAY_BUTTON = "button:has-text('Jugar')"

    # Game page indicators (to verify we're logged in)
    GAME_INDICATORS = [
        "#resourcesbarcomponent",  # Resource bar
        "#planetList",             # Planet list
        "#menuTable",              # Menu
        "#rechts",                 # Right panel
    ]

    def __init__(self, page: Page, context: BrowserContext):
        self.page = page
        self.context = context
        self._game_page: Page | None = None

    def login(self, timeout: int = 30000) -> Page:
        """
        Attempt automatic login by clicking Play buttons.

        Returns the game page if successful.
        Raises LoginError if manual intervention is needed.
        """
        try:
            # Step 1: Click "Jugar" on lobby page
            print("Looking for Play button on lobby...")

            # Navigate directly to accounts page
            accounts_url = "https://lobby.ogame.gameforge.com/es_ES/accounts"
            print(f"Navigating to {accounts_url}...")
            self.page.goto(accounts_url, wait_until="domcontentloaded")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)

            # Find and click "Jugar" button
            print("Looking for Jugar button...")
            play_btn = self.page.locator("button:has-text('Jugar')").first
            play_btn.wait_for(state="visible", timeout=10000)
            print("Found Jugar button, clicking...")

            # Listen for new page (game opens in new tab)
            with self.context.expect_page(timeout=timeout) as new_page_info:
                play_btn.click()

            # Get the new game page
            self._game_page = new_page_info.value
            self._game_page.wait_for_load_state("domcontentloaded")
            print("New tab opened, waiting for game to load...")
            self._game_page.wait_for_timeout(3000)

            # Step 3: Verify we're in the game
            self._game_page.wait_for_load_state("networkidle")

            if self._verify_game_loaded(self._game_page):
                print("Game loaded successfully!")
                return self._game_page
            else:
                raise LoginError("Game page loaded but couldn't verify login")

        except PlaywrightTimeout as e:
            raise LoginError("Login timed out - manual login needed") from e

    def _verify_game_loaded(self, page: Page) -> bool:
        """Check if we're actually in the game."""
        for selector in self.GAME_INDICATORS:
            try:
                page.wait_for_selector(selector, timeout=3000)
                return True
            except PlaywrightTimeout:
                continue
        return False

    def wait_for_manual_login(self) -> Page:
        """
        Wait for user to manually log in.
        User presses Enter after logging in, then we find the game page.
        """
        print("\n" + "="*50)
        print("MANUAL LOGIN REQUIRED")
        print("="*50)
        print("1. Log in with Google in the browser")
        print("2. Click 'Jugar' to enter your universe")
        print("3. Once you see the game, come back here")
        print("="*50)
        input("\nPress Enter when you're in the game... ")

        # Find the game page among all open tabs
        game_page = self._find_game_page()
        if game_page:
            self._game_page = game_page
            print("Game page found!")
            return game_page

        raise LoginError("Couldn't find game page. Make sure you're logged in and try again.")

    def _find_game_page(self) -> Page | None:
        """Find the game page among open tabs."""
        for page in self.context.pages:
            url = page.url
            print(f"  Checking tab: {url[:60]}...")

            # Look for OGame game URLs (contain server ID like s123-es.ogame.gameforge.com)
            if "ogame.gameforge.com" in url and "/game/" in url:
                if self._verify_game_loaded(page):
                    return page

            # Also check by indicators even if URL doesn't match expected pattern
            if "ogame" in url.lower():
                if self._verify_game_loaded(page):
                    return page

        return None

    @property
    def game_page(self) -> Page:
        """Get the game page."""
        if not self._game_page:
            raise RuntimeError("Not logged in yet")
        return self._game_page
