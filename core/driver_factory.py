import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from config.config import BASE_DIR, BROWSER, HEADLESS, IMPLICIT_WAIT
from utils.logger import logger

class DriverFactory:
    @staticmethod
    def get_driver(browser_name: str = None, headless: bool = None) -> webdriver.Chrome:
        browser = (browser_name or BROWSER).lower()
        is_headless = HEADLESS if headless is None else headless

        logger.info(f"Initializing WebDriver: {browser} (Headless: {is_headless})")

        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

            if is_headless:
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920,1080")

            # Project local driver in workspace
            local_driver_exe = BASE_DIR / "drivers" / "chromedriver.exe"
            if local_driver_exe.exists():
                logger.info(f"Using project workspace ChromeDriver: {local_driver_exe}")
                service = ChromeService(executable_path=str(local_driver_exe))
                driver = webdriver.Chrome(service=service, options=options)
                driver.implicitly_wait(IMPLICIT_WAIT)
                return driver

            # Fallback to system PATH / SeleniumManager
            logger.info("Attempting Selenium 4 default SeleniumManager...")
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(IMPLICIT_WAIT)
            return driver

        else:
            raise ValueError(f"Unsupported browser type: {browser}")
