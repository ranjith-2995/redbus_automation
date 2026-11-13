import pytest
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage

class TestRedBusSearch:
    """Test Suite for Redbus Search & Filter Capabilities"""

    def test_search_bus_flow(self, driver, mock_url):
        home_page = HomePage(driver)
        home_page.open_url(mock_url)

        # 1. Search for buses from Bangalore to Chennai
        home_page.search_bus(source="Bangalore", destination="Chennai", days_ahead=1)

        # 2. Verify results are loaded
        results_page = SearchResultsPage(driver)
        assert results_page.is_results_displayed(), "Search results should be displayed after search"

        # 3. Verify available buses count and attributes
        buses = results_page.get_available_buses()
        assert len(buses) > 0, "At least one bus should be available"
        for bus in buses:
            assert bus["fare"] > 0, "Bus fare should be positive"
            assert bus["rating"] >= 1.0, "Bus rating should be valid"

    def test_filter_buses_ac_and_sleeper(self, driver, mock_url):
        home_page = HomePage(driver)
        home_page.open_url(mock_url)
        home_page.search_bus(source="Bangalore", destination="Chennai", days_ahead=1)

        results_page = SearchResultsPage(driver)
        results_page.apply_ac_filter()
        results_page.apply_sleeper_filter()

        filtered_buses = results_page.get_available_buses()
        assert len(filtered_buses) > 0, "Filtered buses should not be empty"
        for bus in filtered_buses:
            assert "A/C" in bus["type"] or "AC" in bus["type"] or "Sleeper" in bus["type"]

