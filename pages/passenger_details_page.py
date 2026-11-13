import time
from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from core.base_page import BasePage
from utils.logger import logger

class PassengerDetailsPage(BasePage):
    NAME_INPUT = (By.ID, "passenger-name")
    GENDER_SELECT = (By.ID, "passenger-gender")
    AGE_INPUT = (By.ID, "passenger-age")
    EMAIL_INPUT = (By.ID, "passenger-email")
    PHONE_INPUT = (By.ID, "passenger-phone")
    BOARDING_SELECT = (By.ID, "boarding-point")
    CONFIRM_BUTTON = (By.ID, "btn-confirm-booking")
    
    # Confirmation elements
    CONFIRMATION_BOX = (By.ID, "booking-confirmation-box")
    PNR_TEXT = (By.ID, "confirmed-pnr")
    DETAILS_TEXT = (By.ID, "confirmed-details")

    def __init__(self, driver):
        super().__init__(driver)

    def fill_passenger_details(self, details: Dict[str, Any]):
        logger.info(f"Filling passenger details for {details.get('name')}")
        self.send_keys(self.NAME_INPUT, str(details.get("name", "Test User")))
        
        gender_elem = self.find_element(self.GENDER_SELECT)
        Select(gender_elem).select_by_value(details.get("gender", "Male"))

        self.send_keys(self.AGE_INPUT, str(details.get("age", 25)))
        self.send_keys(self.EMAIL_INPUT, str(details.get("email", "test@redbus.com")))
        self.send_keys(self.PHONE_INPUT, str(details.get("phone", "9876543210")))
        time.sleep(1)
        self.take_screenshot("passenger_details_filled")

    def select_boarding_point(self, index: int = 0):
        try:
            boarding_elem = self.find_element(self.BOARDING_SELECT)
            select = Select(boarding_elem)
            select.select_by_index(index)
            logger.info(f"Selected boarding point: {select.first_selected_option.text}")
        except Exception as e:
            logger.warning(f"Could not select boarding point: {e}")

    def confirm_booking(self) -> Dict[str, str]:
        logger.info("Clicking Confirm Booking button...")
        self.click(self.CONFIRM_BUTTON)
        time.sleep(2)
        self.take_screenshot("booking_confirmation_result")

        # Verify confirmation box
        self.wait_for_visibility(self.CONFIRMATION_BOX)
        pnr = self.get_text(self.PNR_TEXT)
        details = self.get_text(self.DETAILS_TEXT)
        logger.info(f"Successfully confirmed booking! {pnr} | {details}")
        return {
            "pnr": pnr,
            "details": details,
            "status": "CONFIRMED"
        }

