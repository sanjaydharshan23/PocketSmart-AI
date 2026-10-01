from .gemini_utils import gemini_service, normalize_ai

from .catalog import (
    fallback_home,
    fallback_party,
    fallback_jewelry,
    search_url,
)


def fallback_response(planner, budget, rows, tips):
    recs = []

    for cat, title, price, platform, why in rows:
        recs.append(
            {
                "category": cat,
                "title": title,
                "description": f"Estimated option for your {planner} plan.",
                "estimated_price": round(price, 2),
                "platform": platform,
                "url": search_url(platform, title),
                "why": why,
            }
        )

    return {
        "planner": planner,
        "budget": budget,
        "currency": "INR",
        "allocation": {},
        "summary": (
            "Fallback recommendations are shown because live AI "
            "generation is unavailable or returned insufficient data."
        ),
        "recommendations": recs,
        "tips": tips,
        "ai_generated": False,
        "model": None,
    }


def generate_home(data):
    if gemini_service.available:
        try:
            ai_data = gemini_service.home(data)

            result = normalize_ai(
                ai_data,
                "home",
                data["budget"],
            )

            if result["recommendations"]:
                return result

        except Exception as e:
            print("HOME AI ERROR:", type(e).__name__, str(e))

    return fallback_response(
        "home",
        data["budget"],
        fallback_home(
            data["budget"],
            data.get("style", "modern"),
            data.get("rooms", []),
            data.get("quantities", {}),
        ),
        [
            "Keep a 5–10% buffer for delivery, installation, or price changes.",
            "Compare the linked marketplace results before purchasing.",
        ],
    )


def generate_party(data):
    if gemini_service.available:
        try:
            ai_data = gemini_service.party(data)

            result = normalize_ai(
                ai_data,
                "party",
                data["budget"],
            )

            if result["recommendations"]:
                return result

        except Exception as e:
            print("PARTY AI ERROR:", type(e).__name__, str(e))

    return fallback_response(
        "party",
        data["budget"],
        fallback_party(
            data["budget"],
            data["guests"],
            data.get("event_type", "birthday"),
            data.get("city", ""),
        ),
        [
            "Confirm per-person pricing, taxes, delivery and venue fees directly with providers.",
            "Keep a contingency amount for last-minute guests.",
        ],
    )


def generate_jewelry(data, image_bytes=None, mime_type=None):
    if gemini_service.available:
        try:
            # Current GeminiService.jewelry() accepts only data.
            ai_data = gemini_service.jewelry(data)

            result = normalize_ai(
                ai_data,
                "jewelry",
                data["budget"],
            )

            if result["recommendations"]:
                return result

        except Exception as e:
            print("JEWELRY AI ERROR:", type(e).__name__, str(e))

    return fallback_response(
        "jewelry",
        data["budget"],
        fallback_jewelry(
            data["budget"],
            data.get("occasion", "wedding"),
            data.get("style", "elegant"),
        ),
        [
            "Use the outfit description to refine color and metal choices.",
            "Treat marketplace prices as estimates and verify the listing before buying.",
        ],
    )