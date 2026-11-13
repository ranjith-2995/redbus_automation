import re
from datetime import datetime, timedelta
from typing import Dict, Any

class RedBusIntentParser:
    """
    NLP Intent & Entity Parser for Natural Language Bus Booking Queries.
    Parses sentences like:
    'Book AC sleeper bus from Bangalore to Chennai tomorrow under 1000 rupees'
    """
    
    CITIES = [
        "bangalore", "bengaluru", "chennai", "hyderabad", "mumbai", 
        "pune", "delhi", "coimbatore", "madurai", "kochi", "goa", "mysore"
    ]

    def parse_query(self, user_query: str, apply_defaults: bool = False) -> Dict[str, Any]:
        text = user_query.lower()
        extracted = {
            "source": None,
            "destination": None,
            "days_ahead": 1,
            "bus_type": "ALL",
            "is_ac": None,
            "is_sleeper": None,
            "max_budget": None,
            "preferred_time": "ANY",
            "raw_query": user_query
        }

        # 1. Source and Destination extraction
        # Pattern: from <city> to <city>
        from_to_match = re.search(r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:on|for|tomorrow|today|under|with)|$)', text)
        if from_to_match:
            src_candidate = from_to_match.group(1).strip()
            dest_candidate = from_to_match.group(2).strip()
            for city in self.CITIES:
                if city in src_candidate:
                    extracted["source"] = city.capitalize()
                if city in dest_candidate:
                    extracted["destination"] = city.capitalize()

        # Specific "to <city>" and "from <city>" patterns
        for city in self.CITIES:
            if re.search(rf'\b(?:to|reach|reach\s+to|towards)\s+{city}\b', text):
                extracted["destination"] = city.capitalize()
            if re.search(rf'\b(?:from|leaving|departing|starting\s+from)\s+{city}\b', text):
                extracted["source"] = city.capitalize()

        # Fallback city scan if both not set yet
        if not extracted["source"] or not extracted["destination"]:
            found_cities = []
            for city in self.CITIES:
                pos = text.find(city)
                if pos != -1:
                    found_cities.append((pos, city.capitalize()))
            found_cities.sort(key=lambda x: x[0])
            if len(found_cities) >= 2:
                if not extracted["source"]:
                    extracted["source"] = found_cities[0][1]
                if not extracted["destination"]:
                    extracted["destination"] = found_cities[1][1]
            elif len(found_cities) == 1:
                single_city = found_cities[0][1]
                if re.search(r'\bto\b', text) and not extracted["destination"]:
                    extracted["destination"] = single_city
                elif re.search(r'\bfrom\b', text) and not extracted["source"]:
                    extracted["source"] = single_city

        # 2. Date extraction
        if "today" in text:
            extracted["days_ahead"] = 0
        elif "day after tomorrow" in text:
            extracted["days_ahead"] = 2
        elif "tomorrow" in text:
            extracted["days_ahead"] = 1
        else:
            in_days = re.search(r'in\s+(\d+)\s+days?', text)
            if in_days:
                extracted["days_ahead"] = int(in_days.group(1))

        # 3. Bus Features
        if "non-ac" in text or "non ac" in text:
            extracted["is_ac"] = False
        elif "ac" in text:
            extracted["is_ac"] = True

        if "sleeper" in text:
            extracted["is_sleeper"] = True
        elif "seater" in text:
            extracted["is_sleeper"] = False

        # 4. Budget / Price limit
        budget_match = re.search(r'(?:under|below|less than|within|budget of|max(?:imum)?)\s*(?:rs\.?|inr|₹)?\s*(\d+)', text)
        if not budget_match:
            budget_match = re.search(r'(\d+)\s*(?:rs|rupees|inr|bucks)', text)
        if budget_match:
            extracted["max_budget"] = int(budget_match.group(1))

        # 5. Departure Time Preference
        if any(w in text for w in ["morning", "am"]):
            extracted["preferred_time"] = "MORNING"
        elif any(w in text for w in ["night", "evening", "pm", "late"]):
            extracted["preferred_time"] = "EVENING"

        # Defaults for missing essentials if requested
        if apply_defaults:
            if not extracted["source"]:
                extracted["source"] = "Bangalore"
            if not extracted["destination"]:
                extracted["destination"] = "Chennai"

        return extracted

