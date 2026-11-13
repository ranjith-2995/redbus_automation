import pytest
from ai_assistant.intent_parser import RedBusIntentParser
from ai_assistant.smart_recommender import SmartBusRecommender
from ai_assistant.price_analytics import BusPriceAnalytics
from ai_assistant.conversational_agent import RedBusConversationalAgent
from ai_assistant.bus_comparator import BusComparator
from utils.pdf_ticket_generator import generate_pdf_ticket

class TestAIBookingAssistant:
    """Intermediate Level Test Suite for AI, NLP & Utility Systems"""

    def test_intent_parser_extraction(self):
        parser = RedBusIntentParser()
        query = "Book AC sleeper bus from Bangalore to Chennai tomorrow under 1000 rupees"
        parsed = parser.parse_query(query)

        assert parsed["source"] == "Bangalore", f"Expected Bangalore, got {parsed['source']}"
        assert parsed["destination"] == "Chennai", f"Expected Chennai, got {parsed['destination']}"
        assert parsed["days_ahead"] == 1, "Expected days_ahead=1 for tomorrow"
        assert parsed["is_ac"] is True, "Expected is_ac=True"
        assert parsed["is_sleeper"] is True, "Expected is_sleeper=True"
        assert parsed["max_budget"] == 1000, f"Expected budget 1000, got {parsed['max_budget']}"

    def test_smart_recommender_ranking(self):
        sample_buses = [
            {"id": 1, "name": "Bus High Rate", "type": "A/C Sleeper", "rating": 4.8, "fare": 900},
            {"id": 2, "name": "Bus Over Budget", "type": "A/C Sleeper", "rating": 4.5, "fare": 1800},
            {"id": 3, "name": "Bus Low Rate", "type": "Non-A/C Seater", "rating": 3.2, "fare": 500}
        ]
        intent = {
            "max_budget": 1000,
            "is_ac": True,
            "is_sleeper": True
        }

        ranked = SmartBusRecommender.rank_buses(sample_buses, intent)
        assert len(ranked) == 3
        assert ranked[0]["name"] == "Bus High Rate"
        assert ranked[0]["ai_score"] > ranked[1]["ai_score"]
        assert "AI Recommendation" in ranked[0]["ai_explanation"]

    def test_price_analytics_prediction(self):
        analytics = BusPriceAnalytics()
        prediction = analytics.predict_fair_price(
            distance_km=350,
            is_weekend=False,
            departure_hour=21,
            is_ac=True,
            is_sleeper=True,
            operator_tier=2
        )

        assert "fair_market_price" in prediction
        assert prediction["fair_market_price"] > 300, "Predicted fare should be realistic"
        assert prediction["confidence_score"] >= 0.90
        
        deal_quality = analytics.evaluate_deal_quality(actual_price=500, predicted_price=750)
        assert "Super Deal" in deal_quality

    def test_conversational_agent_multi_turn(self):
        agent = RedBusConversationalAgent()
        
        # Turn 1: Incomplete query
        reply1, ctx1, buses1 = agent.process_message("Hi, I want a bus to Chennai", {})
        assert "departure city" in reply1.lower()
        assert ctx1.get("destination") == "Chennai"
        assert len(buses1) == 0

        # Turn 2: Complete route provided
        reply2, ctx2, buses2 = agent.process_message("Traveling from Bangalore tomorrow under 1000 rs", ctx1)
        assert "Bangalore" in reply2
        assert "Chennai" in reply2
        assert len(buses2) > 0
        assert ctx2.get("source") == "Bangalore"

    def test_pdf_ticket_generator(self):
        ticket_data = {
            "pnr": "RB-99884422",
            "travel_date": "15 Nov 2026",
            "bus_name": "SRS Travels",
            "bus_type": "Volvo AC Sleeper",
            "source": "Bangalore",
            "destination": "Chennai",
            "boarding_point": "Majestic (09:00 PM)",
            "passenger_name": "Ranjith Kumar",
            "passenger_gender": "Male",
            "passenger_age": 24,
            "seat_no": "L2",
            "fare": 950
        }
        pdf_bytes = generate_pdf_ticket(ticket_data)
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 2000, "PDF should have substantial content"
        # Standard PDF magic bytes check
        assert pdf_bytes[:4] == b"%PDF"

    def test_bus_comparator_radar(self):
        fig = BusComparator.generate_radar_chart(["SRS Travels", "KPN Travels"])
        assert fig is not None
        assert len(fig.data) == 2, "Figure should have two polar traces"
