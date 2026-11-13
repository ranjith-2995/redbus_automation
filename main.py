import os
import sys
import time
import subprocess
from pathlib import Path
from config.config import BASE_DIR, PASSENGER_DATA, DEFAULT_SEARCH
from core.driver_factory import DriverFactory
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.seat_selection_page import SeatSelectionPage
from pages.passenger_details_page import PassengerDetailsPage
from ai_assistant.intent_parser import RedBusIntentParser
from ai_assistant.smart_recommender import SmartBusRecommender
from ai_assistant.price_analytics import BusPriceAnalytics
from utils.logger import logger

def banner():
    print("=" * 70)
    print("      REDBUS TICKET BOOKING AUTOMATION & AI SYSTEM")
    print("             Academic & SDET Automation Project")
    print("=" * 70)

def run_automated_booking(headless: bool = False, use_live: bool = False):
    print("\n🚀 Starting End-to-End RedBus Ticket Booking Automation...")
    driver = DriverFactory.get_driver(headless=headless)
    try:
        if use_live:
            target_url = "https://www.redbus.in"
        else:
            html_path = BASE_DIR / "data" / "redbus_mock.html"
            target_url = f"file:///{str(html_path).replace(os.sep, '/')}"

        home = HomePage(driver)
        home.open_url(target_url)

        print(f"📍 Step 1: Searching route {DEFAULT_SEARCH['source']} -> {DEFAULT_SEARCH['destination']}...")
        home.search_bus(
            source=DEFAULT_SEARCH["source"],
            destination=DEFAULT_SEARCH["destination"],
            days_ahead=DEFAULT_SEARCH.get("days_ahead", 1)
        )

        print("🔍 Step 2: Extracting & filtering available buses...")
        results = SearchResultsPage(driver)
        if not results.is_results_displayed():
            print("⚠️ No buses found or page still loading.")
            return

        buses = results.get_available_buses()
        print(f"🚌 Found {len(buses)} active buses.")
        for b in buses:
            print(f"   • [{b['id']}] {b['name']} | {b['type']} | Fare: ₹{b['fare']} | Rating: {b['rating']}★")

        print("⭐ Step 3: Selecting top-rated bus...")
        best_bus = results.select_best_bus_by_rating()

        print(f"💺 Step 4: Selecting available seat in {best_bus['name']}...")
        seat_page = SeatSelectionPage(driver)
        seat_num = seat_page.select_first_available_seat(bus_index=best_bus["id"])
        print(f"   ✅ Seat {seat_num} chosen successfully!")
        seat_page.proceed_to_passenger_details(bus_index=best_bus["id"])

        print("📝 Step 5: Entering Passenger Information...")
        pass_page = PassengerDetailsPage(driver)
        pass_page.fill_passenger_details(PASSENGER_DATA)
        pass_page.select_boarding_point(0)

        print("💳 Step 6: Confirming Booking (Test Mode)...")
        receipt = pass_page.confirm_booking()

        print("\n" + "=" * 50)
        print("🎉 BOOKING CONFIRMATION SUMMARY:")
        print(f"   Status     : {receipt['status']}")
        print(f"   PNR No     : {receipt['pnr']}")
        print(f"   Details    : {receipt['details']}")
        print("=" * 50 + "\n")
        time.sleep(3)

    finally:
        driver.quit()
        print("Driver closed safely.")

def run_ai_assistant():
    print("\n🤖 AI BUS BOOKING & RECOMMENDATION ENGINE")
    print("-" * 50)
    parser = RedBusIntentParser()
    recommender = SmartBusRecommender()
    analytics = BusPriceAnalytics()

    user_query = input("Enter your natural language travel request:\n(e.g., 'Find AC sleeper bus from Bangalore to Chennai tomorrow under 1000 rs'):\n> ")
    if not user_query.strip():
        user_query = "Book AC sleeper bus from Bangalore to Chennai tomorrow under 1000 rupees"
        print(f"Using default query: '{user_query}'")

    parsed = parser.parse_query(user_query)
    print("\n🧠 AI Extracted Travel Intent:")
    for k, v in parsed.items():
        if k != "raw_query":
            print(f"   • {k:<15}: {v}")

    # Simulated bus inventory for ranking
    inventory = [
        {"id": 1, "name": "SRS Travels", "type": "A/C Sleeper (2+1)", "fare": 950, "rating": 4.6},
        {"id": 2, "name": "KPN Travels", "type": "A/C Seater (2+2)", "fare": 750, "rating": 4.3},
        {"id": 3, "name": "Sharma Transports", "type": "Non-A/C Sleeper (2+1)", "fare": 600, "rating": 4.0},
        {"id": 4, "name": "IntrCity SmartBus", "type": "Multi-Axle AC Sleeper", "fare": 1350, "rating": 4.8}
    ]

    ranked = recommender.rank_buses(inventory, parsed)
    print("\n🏆 AI Ranked Recommendations (Best Matches for You):")
    for i, bus in enumerate(ranked, 1):
        print(f"  #{i} {bus['name']} (Score: {bus['ai_score']})")
        print(f"     Fare: ₹{bus['fare']} | Rating: {bus['rating']}★ | Type: {bus['type']}")
        print(f"     💡 {bus['ai_explanation']}")

    # Price Prediction
    pred = analytics.predict_fair_price(distance_km=350, is_weekend=False, departure_hour=21, is_ac=parsed.get("is_ac", True), is_sleeper=parsed.get("is_sleeper", True))
    top_bus_fare = ranked[0]["fare"]
    deal_eval = analytics.evaluate_deal_quality(top_bus_fare, pred["fair_market_price"])

    print("\n📊 Machine Learning Price Analytics:")
    print(f"   • Fair Market Price Predicted : ₹{pred['fair_market_price']}")
    print(f"   • Selected Bus Actual Fare    : ₹{top_bus_fare}")
    print(f"   • Deal Quality Assessment     : {deal_eval}")

def run_pytest_suite():
    print("\n🧪 Running PyTest Automation Suite with HTML Report...")
    subprocess.run([sys.executable, "-m", "pytest"])
    report_file = BASE_DIR / "reports" / "test_report.html"
    print(f"\n✅ Tests Completed! HTML Report available at: {report_file}")

def main():
    banner()
    while True:
        print("\nSelect an option:")
        print("1. Run Live/Local End-to-End Automation (Interactive Browser)")
        print("2. Run Automated PyTest Suite (Generates HTML Report & Screenshots)")
        print("3. Run AI Natural Language Bus Booking Assistant")
        print("4. Launch Streamlit Web Dashboard")
        print("5. Exit")
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            mode = input("Run on Live redbus.in or Local Demo Lab? (1=Local Demo, 2=Live RedBus): ").strip()
            use_live = (mode == "2")
            run_automated_booking(headless=False, use_live=use_live)
        elif choice == "2":
            run_pytest_suite()
        elif choice == "3":
            run_ai_assistant()
        elif choice == "4":
            print("\nStarting Streamlit Dashboard on http://localhost:8501...")
            subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        elif choice == "5":
            print("Exiting. Thank you!")
            break
        else:
            print("Invalid option. Please enter 1 to 5.")

if __name__ == "__main__":
    main()

