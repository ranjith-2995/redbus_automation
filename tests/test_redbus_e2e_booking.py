import pytest
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.seat_selection_page import SeatSelectionPage
from pages.passenger_details_page import PassengerDetailsPage
from config.config import PASSENGER_DATA

class TestRedBusE2EBooking:
    """End-to-End Redbus Ticket Booking Automation Test"""

    def test_complete_booking_workflow(self, driver, mock_url):
        # 1. Open RedBus Page
        home_page = HomePage(driver)
        home_page.open_url(mock_url)

        # 2. Search for route: Bangalore to Chennai
        home_page.search_bus(source="Bangalore", destination="Chennai", days_ahead=1)

        # 3. Search Results & Selection
        results_page = SearchResultsPage(driver)
        assert results_page.is_results_displayed(), "Search results failed to render"
        
        # Select best rated bus
        best_bus = results_page.select_best_bus_by_rating()
        assert best_bus["rating"] >= 4.0, "Expected rating to be at least 4.0"

        # 4. Seat Selection
        seat_page = SeatSelectionPage(driver)
        selected_seat = seat_page.select_first_available_seat(bus_index=best_bus["id"])
        assert selected_seat != "", "Selected seat number should not be empty"
        seat_page.proceed_to_passenger_details(bus_index=best_bus["id"])

        # 5. Fill Passenger Details
        passenger_page = PassengerDetailsPage(driver)
        passenger_page.fill_passenger_details(PASSENGER_DATA)
        passenger_page.select_boarding_point(index=0)

        # 6. Confirm Booking & Verify Assertion
        confirmation = passenger_page.confirm_booking()
        assert confirmation["status"] == "CONFIRMED", "Booking status should be CONFIRMED"
        assert "RB-" in confirmation["pnr"], "Valid PNR starting with 'RB-' should be generated"
        assert PASSENGER_DATA["name"] in confirmation["details"], "Passenger name should match on confirmation slip"

