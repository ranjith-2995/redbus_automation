from typing import List, Dict, Any

class SmartBusRecommender:
    """
    AI Multi-Criteria Decision Making (MCDM) Bus Recommendation Engine.
    Computes a composite utility score:
    Score = 0.40 * NormRating + 0.35 * NormPriceSaving + 0.15 * FeatureMatch + 0.10 * TimeMatch
    """

    @staticmethod
    def rank_buses(buses: List[Dict[str, Any]], user_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not buses:
            return []

        # Find min and max for normalization
        ratings = [b.get("rating", 4.0) for b in buses]
        fares = [b.get("fare", 800) for b in buses]
        
        min_fare, max_fare = min(fares), max(fares)
        min_rating, max_rating = min(ratings), max(ratings)
        fare_range = (max_fare - min_fare) if max_fare > min_fare else 1.0
        rating_range = (max_rating - min_rating) if max_rating > min_rating else 1.0

        budget_limit = user_intent.get("max_budget")
        desired_ac = user_intent.get("is_ac")
        desired_sleeper = user_intent.get("is_sleeper")
        desired_time = user_intent.get("preferred_time", "ANY")

        ranked_results = []
        for bus in buses:
            fare = bus.get("fare", 800)
            rating = bus.get("rating", 4.0)
            bus_type_str = bus.get("type", "").lower()

            # 1. Rating utility (0.0 to 1.0)
            norm_rating = (rating - min_rating) / rating_range

            # 2. Price savings utility (0.0 to 1.0; cheaper gets higher score)
            norm_price = 1.0 - ((fare - min_fare) / fare_range)

            # Budget penalty if it exceeds user's stated budget
            budget_penalty = 0.0
            if budget_limit and fare > budget_limit:
                budget_penalty = 0.35

            # 3. Feature match score
            feature_score = 1.0
            if desired_ac is not None:
                has_ac = "a/c" in bus_type_str or "ac" in bus_type_str
                if has_ac != desired_ac:
                    feature_score -= 0.5

            if desired_sleeper is not None:
                is_sleeper = "sleeper" in bus_type_str
                if is_sleeper != desired_sleeper:
                    feature_score -= 0.5
            feature_score = max(0.0, feature_score)

            # Composite Score (0.0 to 1.0)
            final_score = (
                0.40 * norm_rating +
                0.35 * norm_price +
                0.25 * feature_score -
                budget_penalty
            )
            final_score = round(max(0.0, min(1.0, final_score)), 3)

            # Generate natural language AI reasoning
            reasons = []
            if rating >= 4.4:
                reasons.append(f"Top-tier passenger rating ({rating}★)")
            if fare <= min_fare + 100:
                reasons.append(f"High value fare (₹{fare})")
            if budget_limit and fare <= budget_limit:
                reasons.append(f"Well within your ₹{budget_limit} budget")
            if not reasons:
                reasons.append("Balanced price-to-comfort ratio")

            explanation = "AI Recommendation: " + " & ".join(reasons)

            ranked_results.append({
                **bus,
                "ai_score": final_score,
                "ai_explanation": explanation
            })

        # Sort descending by AI score
        ranked_results.sort(key=lambda x: x["ai_score"], reverse=True)
        return ranked_results

