"""Fleet actions for OGame."""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from ..utils.delay import human_delay


class Fleet:
    """Handle fleet operations."""

    def __init__(self, page: Page):
        self.page = page

    def select_ship(self, ship_name: str, amount: int = 1) -> bool:
        """
        Select a ship by its aria-label and enter the amount.

        Args:
            ship_name: Ship name as it appears in aria-label (e.g., "Segador")
            amount: Number of ships to select
        """
        print(f"Looking for ship '{ship_name}'...")

        try:
            # Find ship by aria-label
            ship_li = self.page.locator(f"li.technology[aria-label*='{ship_name}' i]").first
            ship_li.wait_for(state="visible", timeout=5000)
            print(f"Found '{ship_name}'!")

            # Find the input within this li
            ship_input = ship_li.locator("input").first
            ship_input.wait_for(state="visible", timeout=2000)
            human_delay()
            ship_input.fill(str(amount))
            print(f"Set {amount} x {ship_name}")
            return True

        except PlaywrightTimeout:
            print(f"Ship '{ship_name}' not found!")
            return False

    def click_next(self) -> bool:
        """Click the 'Siguiente' (Next) button."""
        print("Clicking 'Siguiente'...")

        try:
            next_btn = self.page.locator("a:has-text('Siguiente'), button:has-text('Siguiente')").first
            next_btn.wait_for(state="visible", timeout=5000)
            human_delay()
            next_btn.click()
            self.page.wait_for_load_state("networkidle")
            print("Clicked 'Siguiente'")
            return True
        except PlaywrightTimeout:
            print("'Siguiente' button not found!")
            return False

    def set_coordinates(self, galaxy: str = None, system: str = None, position: str = None) -> bool:
        """
        Set destination coordinates. Only fills in the values provided.

        Args:
            galaxy: Galaxy number (1st input)
            system: System number (2nd input)
            position: Position number (3rd input) - use "16" for expeditions
        """
        print("Setting coordinates...")

        try:
            # Find the coordinates section
            coords_label = self.page.locator("text=Coordenadas:").first
            coords_label.wait_for(state="visible", timeout=5000)

            # Find the parent/container and get the inputs
            # The inputs are typically in a nearby container
            coords_container = coords_label.locator("xpath=ancestor::*[.//input][1]")
            inputs = coords_container.locator("input[type='text'], input[type='number']")

            if inputs.count() >= 3:
                if galaxy is not None:
                    human_delay()
                    inputs.nth(0).click()
                    inputs.nth(0).press("Meta+a")
                    inputs.nth(0).type(str(galaxy))
                    print(f"  Galaxy: {galaxy}")
                if system is not None:
                    human_delay()
                    inputs.nth(1).click()
                    inputs.nth(1).press("Meta+a")
                    inputs.nth(1).type(str(system))
                    print(f"  System: {system}")
                if position is not None:
                    human_delay()
                    inputs.nth(2).click()
                    inputs.nth(2).press("Meta+a")
                    inputs.nth(2).type(str(position))
                    print(f"  Position: {position}")
                return True
            else:
                print(f"Expected 3 coordinate inputs, found {inputs.count()}")
                return False

        except PlaywrightTimeout:
            print("Coordinates section not found!")
            return False

    def select_expedition(self) -> bool:
        """Click the 'Expedición' mission button."""
        print("Looking for 'Expedición' button...")

        try:
            exp_btn = self.page.locator("a:has-text('Expedición'), button:has-text('Expedición')").first
            exp_btn.wait_for(state="visible", timeout=10000)
            human_delay()
            exp_btn.click()
            print("Clicked 'Expedición'")
            return True
        except PlaywrightTimeout:
            print("'Expedición' button not found!")
            return False

    def send_fleet(self) -> bool:
        """Click the 'Enviar Flota' button to dispatch the fleet."""
        print("Looking for 'Enviar Flota' button...")

        try:
            send_btn = self.page.locator("a:has-text('Enviar Flota'), button:has-text('Enviar Flota')").first
            send_btn.wait_for(state="visible", timeout=10000)
            human_delay()
            send_btn.click()
            self.page.wait_for_load_state("networkidle")
            print("Fleet sent!")
            return True
        except PlaywrightTimeout:
            print("'Enviar Flota' button not found!")
            return False

    def get_expedition_slots(self) -> tuple[int, int]:
        """
        Get current and max expedition slots from the fleet page.

        Returns:
            Tuple of (current_expeditions, max_expeditions)
            e.g., (2, 6) means 2 expeditions running, 6 max
        """
        print("Checking expedition slots...")

        try:
            # Look for "Expediciones" text and get the sibling/following element with the counter
            exp_element = self.page.locator("text=Expediciones").first
            exp_element.wait_for(state="visible", timeout=5000)

            # Get the counter that's to the RIGHT of "Expediciones"
            # Try finding the next sibling or following element
            counter = exp_element.locator("xpath=following-sibling::*[1]").first
            counter_text = counter.text_content(timeout=2000)
            print(f"Found counter to the right: {counter_text}")

            # Parse "X/Y" pattern
            import re
            match = re.search(r"(\d+)\s*/\s*(\d+)", counter_text)
            if match:
                current = int(match.group(1))
                maximum = int(match.group(2))
                print(f"Expeditions: {current}/{maximum} (available: {maximum - current})")
                return (current, maximum)

        except Exception as e:
            print(f"First method failed: {e}")

        # Fallback: look for pattern after "Expediciones" in text
        try:
            # Get text content after "Expediciones"
            parent = self.page.locator("*:has(> *:text('Expediciones'))").first
            full_text = parent.text_content(timeout=2000)
            print(f"Parent text: {full_text}")

            import re
            # Find the pattern AFTER "Expediciones" - use [\s\S]*? to match newlines
            match = re.search(r"Expediciones[\s\S]*?(\d+)\s*/\s*(\d+)", full_text)
            if match:
                current = int(match.group(1))
                maximum = int(match.group(2))
                print(f"Expeditions: {current}/{maximum} (available: {maximum - current})")
                return (current, maximum)
        except Exception as e:
            print(f"Fallback failed: {e}")

        print("Could not determine expedition slots, defaulting to 0 available")
        return (0, 0)  # Safe default: assume no slots available  # Safe default: assume no slots available  # Safe default: assume no slots available  # Safe default: assume no slots available

    def get_available_expeditions(self) -> int:
        """Get the number of expedition slots available."""
        current, maximum = self.get_expedition_slots()
        return maximum - current

    def _send_single_attack(self, ships: dict[str, int], coords: tuple[int, int, int]) -> bool:
        """
        Send a single attack (assumes we're already on Flota page).

        Args:
            ships: Dictionary of ship_name -> amount
            coords: Tuple of (galaxy, system, position)

        Returns:
            True if attack was sent successfully
        """
        from .navigation import Navigation
        nav = Navigation(self.page)

        galaxy, system, position = coords
        print(f"Target: [{galaxy}:{system}:{position}]")

        # Select ships
        for ship_name, amount in ships.items():
            if not self.select_ship(ship_name, amount):
                print(f"Failed to select {ship_name}")
                return False

        # Click next
        if not self.click_next():
            return False

        # Set full coordinates
        if not self.set_coordinates(galaxy=str(galaxy), system=str(system), position=str(position)):
            return False

        # Select attack mission
        if not self.select_attack():
            return False

        # Send the fleet
        if not self.send_fleet():
            return False

        print(f"Attack sent to [{galaxy}:{system}:{position}]!")

        # Go back to Flota for next attack
        nav.click_menu_by_text("Flota")

        return True

    def select_attack(self) -> bool:
        """Click the 'Atacar' mission button."""
        print("Looking for 'Atacar' button...")

        try:
            attack_btn = self.page.locator("a:has-text('Atacar'), button:has-text('Atacar')").first
            attack_btn.wait_for(state="visible", timeout=10000)
            human_delay()
            attack_btn.click()
            print("Clicked 'Atacar'")
            return True
        except PlaywrightTimeout:
            print("'Atacar' button not found!")
            return False

    def send_farm_attacks(self, planet: str, ships: dict[str, int], targets: list[tuple[int, int, int]]) -> int:
        """
        Send farm attacks to multiple coordinates.

        Args:
            planet: Name of the planet to send from
            ships: Dictionary of ship_name -> amount
            targets: List of coordinate tuples [(galaxy, system, position), ...]

        Returns:
            Number of attacks successfully sent
        """
        from .navigation import Navigation
        nav = Navigation(self.page)

        print(f"\n{'='*50}")
        print(f"Starting farm attacks from {planet}: {len(targets)} targets")
        print(f"{'='*50}\n")

        # Navigate to planet and fleet menu once
        if not nav.select_planet(planet):
            return 0
        if not nav.click_menu_by_text("Flota"):
            return 0

        sent = 0
        for i, coords in enumerate(targets):
            print(f"\n--- Attack {i + 1} of {len(targets)} ---")
            if self._send_single_attack(ships, coords):
                sent += 1
            else:
                print(f"Failed to send attack to {coords}")

        print(f"\n{'='*50}")
        print(f"Farm attacks complete! Sent {sent}/{len(targets)}")
        print(f"{'='*50}\n")
        return sent

    def send_expedition(self, planet: str, ships: dict[str, int]) -> bool:
        """
        Send an expedition with the specified ships from a planet.

        Args:
            planet: Name of the planet to send from (e.g., "Imladris")
            ships: Dictionary of ship_name -> amount (e.g., {"Segador": 1, "Explorador": 1})

        Returns:
            True if expedition was sent successfully
        """
        from .navigation import Navigation
        nav = Navigation(self.page)

        print(f"\n=== Sending Expedition from {planet} ===")

        # Navigate to planet
        if not nav.select_planet(planet):
            return False

        # Go to fleet menu
        if not nav.click_menu_by_text("Flota"):
            return False

        # Select ships
        for ship_name, amount in ships.items():
            if not self.select_ship(ship_name, amount):
                print(f"Failed to select {ship_name}")
                return False

        # Click next
        if not self.click_next():
            return False

        # Set position to 16 (expedition)
        if not self.set_coordinates(position="16"):
            return False

        # Select expedition mission
        if not self.select_expedition():
            return False

        # Send the fleet
        if not self.send_fleet():
            return False

        print("=== Expedition Sent! ===\n")
        return True

    def debug_list_ships(self):
        """Debug: Print info about all ship slots found."""
        print("\n=== DEBUG: Listing all ship slots ===")

        ships = self.page.locator("li.technology")
        count = ships.count()
        print(f"Found {count} ships:")

        for i in range(count):
            ship = ships.nth(i)
            try:
                label = ship.get_attribute("aria-label")
                status = ship.get_attribute("data-status")
                print(f"  [{i+1}]: {label} (status: {status})")
            except:
                print(f"  [{i+1}]: (couldn't read)")

        print("=== END DEBUG ===\n")
