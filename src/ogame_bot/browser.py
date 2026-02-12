"""Browser management using Playwright."""

from playwright.sync_api import sync_playwright, BrowserContext, Page

from .config import OGameConfig


class BrowserManager:
    """Manages Playwright browser lifecycle using Chrome with existing profile."""

    def __init__(self, config: OGameConfig):
        self.config = config
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def __enter__(self) -> "BrowserManager":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self) -> Page:
        """Start Chrome with existing user profile and return page."""
        self._playwright = sync_playwright().start()

        # Use persistent context to access existing Chrome profile with Google login
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.config.chrome_user_data_dir,
            channel="chrome",  # Use installed Chrome, not Chromium
            headless=self.config.headless,
            slow_mo=self.config.slow_mo,
            viewport={"width": 1920, "height": 1080},
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        )

        # Always create a fresh page for navigation
        self._page = self._context.new_page()

        return self._page

    def stop(self):
        """Close browser and cleanup."""
        if self._context:
            self._context.close()
        if self._playwright:
            self._playwright.stop()

    @property
    def page(self) -> Page:
        """Get current page."""
        if not self._page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Get browser context."""
        if not self._context:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._context

    def goto_lobby(self) -> Page:
        """Navigate to OGame lobby. Returns the page with the lobby."""
        url = self.config.lobby_url

        # Debug: show all tabs before
        print(f"Tabs before navigation: {[p.url for p in self._context.pages]}")

        print(f"Navigating to {url}...")
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

        # Wait a moment for any redirects/popups
        self.page.wait_for_timeout(2000)

        # Debug: show all tabs after
        print(f"Tabs after navigation: {[p.url for p in self._context.pages]}")

        # Check if lobby opened in a different tab
        for page in self._context.pages:
            if "lobby.ogame" in page.url:
                print(f"Found lobby at: {page.url}")
                self._page = page
                page.bring_to_front()
                return page

        print(f"Current URL: {self.page.url}")
        return self.page
