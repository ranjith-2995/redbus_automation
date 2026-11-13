from typing import Dict, Any, List, Tuple
from .intent_parser import RedBusIntentParser
from .smart_recommender import SmartBusRecommender

class RedBusConversationalAgent:
    """
    Stateful Multi-Turn Dialogue Agent for Bus Booking.
    Maintains dialogue state, handles clarification prompts, and presents recommended trips.
    """

    DEFAULT_INVENTORY = [
        {"id": 1, "name": "SRS Travels", "type": "A/C Sleeper (2+1) Multi-Axle", "fare": 950, "rating": 4.6, "dep": "21:00", "arr": "03:30", "seats": 18, "amenities": ["WiFi", "Blanket", "Charging Point", "Water Bottle"]},
        {"id": 2, "name": "KPN Travels", "type": "Bharat Benz A/C Seater (2+2)", "fare": 750, "rating": 4.3, "dep": "07:30", "arr": "13:45", "seats": 24, "amenities": ["Charging Point", "Reading Light", "Water Bottle"]},
        {"id": 3, "name": "Sharma Transports", "type": "Non-A/C Sleeper (2+1)", "fare": 600, "rating": 4.0, "dep": "22:15", "arr": "05:15", "seats": 12, "amenities": ["Blanket", "Emergency Exit"]},
        {"id": 4, "name": "IntrCity SmartBus", "type": "Club Class Volvo AC Sleeper", "fare": 1250, "rating": 4.8, "dep": "22:30", "arr": "05:00", "seats": 10, "amenities": ["WiFi", "Live Tracking", "Blanket", "Snacks", "Clean Washroom"]}
    ]

    def __init__(self):
        self.parser = RedBusIntentParser()

    def process_message(self, user_msg: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Takes user input and current session state.
        Returns: (agent_reply, updated_context, matching_buses)
        """
        ctx = dict(context or {})
        text = user_msg.strip()

        # Update intent from current message without forcing defaults
        parsed = self.parser.parse_query(text, apply_defaults=False)
        
        # Merge into session state
        for key in ["source", "destination", "is_ac", "is_sleeper", "max_budget", "preferred_time", "days_ahead"]:
            if parsed.get(key) is not None:
                ctx[key] = parsed[key]

        # Determine dialogue phase
        src = ctx.get("source")
        dest = ctx.get("destination")

        if not src and not dest:
            reply = "Hello! 👋 I'm your **RedBus AI Travel Concierge**. Where would you like to travel? (e.g., *'Find buses from Bangalore to Chennai tomorrow'*)"
            return reply, ctx, []

        if not src:
            reply = f"I see you want to travel to **{dest}**. What is your departure city?"
            return reply, ctx, []

        if not dest:
            reply = f"Traveling from **{src}** — that sounds great! Which city are you heading to?"
            return reply, ctx, []

        # If both Source and Destination are available, rank matching buses
        ranked_buses = SmartBusRecommender.rank_buses(self.DEFAULT_INVENTORY, ctx)

        budget_str = f" under ₹{ctx['max_budget']}" if ctx.get("max_budget") else ""
        type_str = ""
        if ctx.get("is_ac") and ctx.get("is_sleeper"):
            type_str = " AC Sleeper"
        elif ctx.get("is_ac"):
            type_str = " AC"
        elif ctx.get("is_sleeper"):
            type_str = " Sleeper"

        reply = (
            f"Here are the top-ranked buses from **{src}** to **{dest}**{type_str}{budget_str}. "
            f"Our AI algorithm evaluated customer ratings, on-time performance, and fare savings to rank the best options below:"
        )

        return reply, ctx, ranked_buses
