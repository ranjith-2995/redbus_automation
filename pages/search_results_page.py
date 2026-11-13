import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from core.base_page import BasePage
from utils.logger import logger

class SearchResultsPage(BasePage):
    # Locators
    SEARCH_HEADING = (By.ID, "search-heading")
    BUS_CARDS = (By.CLASS_NAME, "bus-card")
    FILTER_AC = (By.ID, "filter-ac")
    FILTER_SLEEPER = (By.ID, "filter-sleeper")
    FILTER_SEATER = (By.ID, "filter-seater")
    
    # Generic selectors for bus card fields
    BUS_NAME = (By.CLASS_NAME, "bus-name")
    BUS_TYPE = (By.CLASS_NAME, "bus-type")
    RATING_BADGE = (By.CLASS_NAME, "rating-badge")
    BUS_FARE = (By.CLASS_NAME, "bus-fare")
    SEATS_LEFT = (By.CLASS_NAME, "seats-left")
    VIEW_SEATS_BTN = (By.CLASS_NAME, "btn-view-seats")

    def __init__(self, driver):
        super().__init__(driver)

    def is_results_displayed(self) -> bool:
        cards = self.find_elements(self.BUS_CARDS)
        logger.info(f"Detected {len(cards)} bus results on page")
        return len(cards) > 0

    def apply_ac_filter(self):
        logger.info("Applying 'AC Buses' filter")
        checkbox = self.find_element(self.FILTER_AC)
        if not checkbox.is_selected():
            self.click(self.FILTER_AC)
        time.sleep(1)

    def apply_sleeper_filter(self):
        logger.info("Applying 'Sleeper' filter")
        checkbox = self.find_element(self.FILTER_SLEEPER)
        if not checkbox.is_selected():
            self.click(self.FILTER_SLEEPER)
        time.sleep(1)

    def get_available_buses(self) -> List[Dict[str, Any]]:
        buses = []
        cards = self.find_elements(self.BUS_CARDS)
        for idx, card in enumerate(cards, 1):
            try:
                if not card.is_displayed():
                    continue
                name = card.find_element(*self.BUS_NAME).text.strip()
                bus_type = card.find_element(*self.BUS_TYPE).text.strip()
                rating_raw = card.find_element(*self.RATING_BADGE).text.strip()
                fare_raw = card.find_element(*self.BUS_FARE).text.strip()
                seats_raw = card.find_element(*self.SEATS_LEFT).text.strip()

                rating = float(rating_raw.replace("★", "").strip()) if "★" in rating_raw or rating_raw.replace(".", "").isdigit() else 4.0
                fare = int(''.join(filter(str.isdigit, fare_raw))) if any(c.isdigit() for c in fare_raw) else 0

                buses.append({
                    "id": idx,
                    "name": name,
                    "type": bus_type,
                    "rating": rating,
                    "fare": fare,
                    "seats_info": seats_raw,
                    "element": card
                })
            except Exception as e:
                logger.debug(f"Error parsing bus card {idx}: {e}")
        
        logger.info(f"Extracted information for {len(buses)} active buses")
        return buses

    def select_bus_by_index(self, bus_index: int = 1):
        logger.info(f"Selecting bus #{bus_index} to view seats")
        btn_locator = (By.ID, f"view-seats-{bus_index}")
        self.scroll_to_element(btn_locator)
        self.click(btn_locator)
        time.sleep(1.5)
        self.take_screenshot(f"view_seats_bus_{bus_index}")

    def select_best_bus_by_rating(self) -> Dict[str, Any]:
        buses = self.get_available_buses()
        if not buses:
            raise RuntimeError("No available buses found matching criteria!")
        best_bus = max(buses, key=lambda b: b["rating"])
        logger.info(f"Highest rated bus is {best_bus['name']} (Rating: {best_bus['rating']}, Fare: ₹{best_bus['fare']})")
        self.select_bus_by_index(best_bus["id"])
        return best_bus

