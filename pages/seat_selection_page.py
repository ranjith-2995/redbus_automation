import time
from typing import Optional
from selenium.webdriver.common.by import By
from core.base_page import BasePage
from utils.logger import logger

class SeatSelectionPage(BasePage):
    AVAILABLE_SEATS = (By.XPATH, "//div[contains(@class,'seat-item') and not(contains(@class,'booked'))]")
    PROCEED_BUTTONS = (By.XPATH, "//button[contains(@id,'proceed-seats') or contains(text(),'PROCEED TO BOOK')]")

    def __init__(self, driver):
        super().__init__(driver)

    def select_first_available_seat(self, bus_index: int = 1) -> str:
        logger.info(f"Selecting an available seat in bus #{bus_index}")
        # Look for seats within the current panel or generally
        panel_locator = (By.ID, f"seats-panel-{bus_index}")
        self.wait_for_visibility(panel_locator)

        seat_elements = self.find_elements((By.XPATH, f"//div[@id='seats-panel-{bus_index}']//div[contains(@class,'seat-item') and not(contains(@class,'booked'))]"))
        if not seat_elements:
            # Fallback to any unbooked seat
            seat_elements = self.find_elements(self.AVAILABLE_SEATS)

        if not seat_elements:
            raise RuntimeError("No available seats found in this bus!")

        target_seat = seat_elements[0]
        seat_num = target_seat.text.strip()
        logger.info(f"Clicking available seat: {seat_num}")
        
        target_seat.click()
        time.sleep(1)
        self.take_screenshot(f"seat_selected_{seat_num}")
        return seat_num

    def proceed_to_passenger_details(self, bus_index: int = 1):
        logger.info("Proceeding to passenger details page...")
        proceed_btn = (By.ID, f"proceed-seats-{bus_index}")
        self.click(proceed_btn)
        time.sleep(1.5)
        self.take_screenshot("navigated_to_passenger_details")

