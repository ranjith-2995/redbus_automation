import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from core.base_page import BasePage
from utils.logger import logger

class HomePage(BasePage):
    # Locators (supporting both live Redbus and demo simulation)
    SRC_INPUT = (By.ID, "src")
    DEST_INPUT = (By.ID, "dest")
    DATE_INPUT = (By.ID, "travel_date")
    SEARCH_BUTTON = (By.ID, "search_button")
    
    # Live RedBus specific locators
    LIVE_SRC_INPUT = (By.XPATH, "//input[@id='src'] | //div[contains(@class,'src')]//input")
    LIVE_DEST_INPUT = (By.XPATH, "//input[@id='dest'] | //div[contains(@class,'dest')]//input")
    LIVE_SUGGESTION_ITEM = (By.XPATH, "//ul[contains(@class, 'autoFill')]//li | //div[contains(@class, 'suggestion')]//li | //ul[@id='src-suggestions']//li")
    LIVE_DATE_PICKER = (By.XPATH, "//div[contains(@class, 'date')] | //span[contains(@class, 'date')]")

    def __init__(self, driver):
        super().__init__(driver)

    def enter_source(self, source_city: str):
        logger.info(f"Entering source city: {source_city}")
        try:
            self.send_keys(self.SRC_INPUT, source_city)
            time.sleep(1)
            # Select first suggestion if available
            suggestions = self.find_elements((By.XPATH, "//ul[contains(@class,'auto-suggest-list')]//li[not(@style='display: none;')] | //ul[contains(@class,'autoFill')]//li"))
            if suggestions:
                suggestions[0].click()
                logger.info(f"Selected source suggestion: {source_city}")
            else:
                self.find_element(self.SRC_INPUT).send_keys(Keys.ENTER)
        except Exception as e:
            logger.warning(f"Fallback source input method triggered: {e}")
            el = self.find_element(self.SRC_INPUT)
            el.clear()
            el.send_keys(source_city)

    def enter_destination(self, dest_city: str):
        logger.info(f"Entering destination city: {dest_city}")
        try:
            # Click destination field directly
            dest_el = self.find_element(self.DEST_INPUT)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dest_el)
            dest_el.click()
            dest_el.clear()
            dest_el.send_keys(dest_city)
            time.sleep(1)
            suggestions = self.find_elements((By.XPATH, "//ul[@id='dest-suggestions']//li[not(@style='display: none;')] | //ul[contains(@class,'autoFill')]//li"))
            if suggestions:
                suggestions[0].click()
                logger.info(f"Selected destination suggestion: {dest_city}")
            else:
                dest_el.send_keys(Keys.ENTER)
        except Exception as e:
            logger.warning(f"Fallback destination input method: {e}")
            dest_el = self.find_element(self.DEST_INPUT)
            self.driver.execute_script("arguments[0].value = arguments[1];", dest_el, dest_city)

    def select_date(self, days_ahead: int = 1):
        target_date = datetime.now() + timedelta(days=days_ahead)
        formatted_date = target_date.strftime("%Y-%m-%d")
        logger.info(f"Selecting travel date: {formatted_date} ({days_ahead} day(s) from now)")
        
        try:
            date_field = self.find_element(self.DATE_INPUT)
            # Set via JavaScript in case the date picker input is readonly
            self.driver.execute_script("arguments[0].value = arguments[1];", date_field, formatted_date)
        except Exception as e:
            logger.warning(f"Date selection fallback triggered: {e}")

    def click_search(self):
        logger.info("Clicking Search Buses button")
        self.take_screenshot("before_search_click")
        self.click(self.SEARCH_BUTTON)
        time.sleep(2)
        self.take_screenshot("after_search_click")

    def search_bus(self, source: str, destination: str, days_ahead: int = 1):
        self.enter_source(source)
        self.enter_destination(destination)
        self.select_date(days_ahead)
        self.click_search()
