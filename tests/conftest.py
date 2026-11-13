import pytest
import os
from pathlib import Path
from core.driver_factory import DriverFactory
from config.config import BASE_DIR, HEADLESS

@pytest.fixture(scope="function")
def driver():
    """Initializes and yields WebDriver instance, ensuring safe cleanup."""
    # Run headless by default during pytest suite runs for speed and stability
    driver_instance = DriverFactory.get_driver(headless=HEADLESS)
    yield driver_instance
    try:
        driver_instance.quit()
    except Exception:
        pass

@pytest.fixture(scope="session")
def mock_url():
    """Returns the local URL for the offline simulated redBus page."""
    html_path = BASE_DIR / "data" / "redbus_mock.html"
    return f"file:///{str(html_path).replace(os.sep, '/')}"

def pytest_html_report_title(report):
    report.title = "RedBus Automation & AI Project - Test Execution Report"

