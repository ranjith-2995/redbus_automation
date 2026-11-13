import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from config.config import EXPLICIT_WAIT, SCREENSHOTS_DIR
from utils.logger import logger

class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = EXPLICIT_WAIT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open_url(self, url: str):
        logger.info(f"Navigating to URL: {url}")
        self.driver.get(url)

    def find_element(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        wait_time = timeout or self.timeout
        return WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(locator)
        )

    def find_elements(self, locator: tuple, timeout: Optional[int] = None) -> List[WebElement]:
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_all_elements_located(locator)
            )
        except TimeoutException:
            return []

    def wait_for_visibility(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        wait_time = timeout or self.timeout
        return WebDriverWait(self.driver, wait_time).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_clickable(self, locator: tuple, timeout: Optional[int] = None) -> WebElement:
        wait_time = timeout or self.timeout
        return WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable(locator)
        )

    def click(self, locator: tuple, timeout: Optional[int] = None):
        wait_time = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
        except (ElementClickInterceptedException, TimeoutException):
            logger.warning(f"Standard click failed for locator {locator}, falling back to JavaScript click")
            element = self.find_element(locator, timeout=wait_time)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", element)

    def send_keys(self, locator: tuple, text: str, clear_first: bool = True):
        element = self.wait_for_visibility(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        try:
            element = self.wait_for_visibility(locator)
            return element.text.strip()
        except TimeoutException:
            return ""

    def is_displayed(self, locator: tuple, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def scroll_to_element(self, locator: tuple):
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)

    def scroll_by(self, x: int = 0, y: int = 500):
        self.driver.execute_script(f"window.scrollBy({x}, {y});")
        time.sleep(0.5)

    def take_screenshot(self, name: str = "screenshot") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        self.driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

