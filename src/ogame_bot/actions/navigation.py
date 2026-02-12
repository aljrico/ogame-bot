"""Navigation actions for OGame."""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from ..utils.delay import human_delay


class Navigation:
    """Handle navigation within the game."""

    # Selectors
    PLANET_LIST = "#planetList"
    PLANET_ITEM = ".smallplanet"
    PLANET_NAME = ".planet-name"

    def __init__(self, page: Page):
        self.page = page

    def select_planet(self, name: str) -> bool:
        """
        Select a planet by name.
        Returns True if successful.
        """
        print(f"Looking for planet '{name}'...")

        # Find all planets in the list
        planets = self.page.locator(f"{self.PLANET_LIST} {self.PLANET_ITEM}")

        count = planets.count()
        print(f"Found {count} planets")

        for i in range(count):
            planet = planets.nth(i)
            planet_name_el = planet.locator(self.PLANET_NAME)

            try:
                planet_name = planet_name_el.text_content(timeout=2000)
                print(f"  Planet {i+1}: {planet_name}")

                if planet_name and name.lower() in planet_name.lower():
                    print(f"Found '{name}'! Clicking...")
                    human_delay()
                    planet.click()
                    self.page.wait_for_load_state("networkidle")
                    print(f"Selected planet: {name}")
                    return True
            except PlaywrightTimeout:
                continue

        print(f"Planet '{name}' not found!")
        return False

    def go_to_menu(self, menu: str) -> bool:
        """
        Navigate to a menu item (e.g., 'fleet', 'overview', 'resources').
        """
        menu_map = {
            "overview": "overview",
            "resources": "supplies",
            "facilities": "facilities",
            "research": "research",
            "shipyard": "shipyard",
            "defense": "defense",
            "fleet": "fleetdispatch",
            "galaxy": "galaxy",
        }

        menu_id = menu_map.get(menu.lower())
        if not menu_id:
            print(f"Unknown menu: {menu}")
            return False

        print(f"Navigating to {menu}...")
        menu_link = self.page.locator(f"#menuTable a[data-component='{menu_id}']")

        try:
            human_delay()
            menu_link.click()
            self.page.wait_for_load_state("networkidle")
            print(f"Now in: {menu}")
            return True
        except PlaywrightTimeout:
            print(f"Failed to navigate to {menu}")
            return False

    def get_current_planet(self) -> str | None:
        """Get the name of the currently selected planet."""
        try:
            # The selected planet has a specific class or state
            selected = self.page.locator(f"{self.PLANET_LIST} {self.PLANET_ITEM}.hightlightPlanet, {self.PLANET_LIST} {self.PLANET_ITEM}.active")
            if selected.count() > 0:
                name = selected.first.locator(self.PLANET_NAME).text_content(timeout=2000)
                return name.strip() if name else None
        except:
            pass
        return None

    def click_menu_by_text(self, text: str) -> bool:
        """
        Click on a menu item by its visible text.
        """
        print(f"Looking for menu '{text}'...")

        try:
            # Look for the text in the menu area
            menu_item = self.page.locator(f"#menuTable >> text='{text}'").first
            menu_item.wait_for(state="visible", timeout=5000)
            human_delay()
            menu_item.click()
            self.page.wait_for_load_state("networkidle")
            print(f"Clicked on '{text}'")
            return True
        except PlaywrightTimeout:
            print(f"Menu '{text}' not found!")
            return False
