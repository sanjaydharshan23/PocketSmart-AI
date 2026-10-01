import json
from typing import Any

from google import genai
from google.genai import types

from .catalog import search_url
from app.config import settings


class GeminiService:

    def __init__(self):
        self.client = None

        if settings.gemini_api_key and settings.ai_enabled:
            try:
                self.client = genai.Client(
                    api_key=settings.gemini_api_key
                )

                print("Gemini client initialized successfully")

            except Exception as e:
                print("Gemini client initialization failed:")
                print("ERROR TYPE:", type(e).__name__)
                print("ERROR:", str(e))

                self.client = None

        else:
            print("Gemini is disabled or API key is missing")
            print(
                "API KEY EXISTS:",
                bool(settings.gemini_api_key)
            )
            print(
                "AI ENABLED:",
                settings.ai_enabled
            )

    @property
    def available(self) -> bool:
        return self.client is not None

    def call(
        self,
        prompt: str,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any]:

        if not self.client:
            raise RuntimeError(
                "Gemini is not configured. "
                "Check GEMINI_API_KEY and AI_ENABLED."
            )

        contents: list[Any] = [prompt]

        # Optional image input
        if image_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type or "image/jpeg",
                )
            )

        try:
            print()
            print("========== GEMINI CALL START ==========")
            print("MODEL:", settings.gemini_model)
            print(
                "API KEY EXISTS:",
                bool(settings.gemini_api_key)
            )
            print(
                "AI ENABLED:",
                settings.ai_enabled
            )

            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                ),
            )

            # Get text response
            text = response.text or "{}"

            print("GEMINI RAW RESPONSE:")
            print(text)

            # Clean markdown code fences if Gemini returns them
            text = text.strip()

            if text.startswith("```json"):
                text = text[7:]

            elif text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # Parse JSON
            result = json.loads(text)

            print("GEMINI JSON PARSED SUCCESSFULLY")
            print("========== GEMINI CALL END ==========")
            print()

            return result

        except Exception as e:
            print()
            print("========== GEMINI ERROR ==========")
            print("ERROR TYPE:", type(e).__name__)
            print("ERROR:", str(e))
            print("===================================")
            print()

            raise

    # ---------------------------------------------------------
    # HOME PLANNER
    # ---------------------------------------------------------

    def home(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = f"""
You are PocketSmart AI's home interior budget planner.

Return ONLY valid JSON.

Do not return markdown.
Do not return ```json.
Do not add explanations outside JSON.

User budget: INR {data.get("budget", 0)}

Rooms:
{data.get("rooms", [])}

Style:
{data.get("style", "modern")}

Quantities:
{data.get("quantities", {})}

Create practical home interior recommendations.

Return exactly this structure:

{{
    "recommendations": [
        {{
            "category": "string",
            "title": "string",
            "description": "string",
            "estimated_price": 0,
            "platform": "string",
            "url": "string"
        }}
    ],
    "tips": [
        "string"
    ]
}}

Rules:

1. Keep recommendations within the user's budget.
2. Give realistic Indian prices in INR.
3. Give practical buying suggestions.
4. Give useful budgeting tips.
5. Do not invent extremely expensive products.
6. estimated_price must be a number.
7. recommendations must be a JSON array.
8. tips must be a JSON array.
9. Return at least 3 recommendations when possible.
"""

        return self.call(prompt)

    # ---------------------------------------------------------
    # PARTY PLANNER
    # ---------------------------------------------------------

    def party(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = f"""
You are PocketSmart AI's party planner.

Return ONLY valid JSON.

Do not return markdown.
Do not return ```json.
Do not add explanations outside JSON.

Budget: INR {data.get("budget", 0)}

Guests:
{data.get("guests", 0)}

Event type:
{data.get("event_type", "party")}

City:
{data.get("city", "")}

Create practical party recommendations.

Return exactly this structure:

{{
    "recommendations": [
        {{
            "category": "string",
            "title": "string",
            "description": "string",
            "estimated_price": 0,
            "platform": "string",
            "url": "string"
        }}
    ],
    "tips": [
        "string"
    ]
}}

Rules:

1. Keep everything within the budget.
2. Use realistic Indian prices.
3. Consider the number of guests.
4. Give practical party planning tips.
5. estimated_price must be a number.
6. recommendations must be a JSON array.
7. tips must be a JSON array.
8. Return at least 4 recommendations when possible.
"""

        return self.call(prompt)

    # ---------------------------------------------------------
    # JEWELRY PLANNER
    # ---------------------------------------------------------

    def jewelry(
        self,
        data: dict[str, Any],
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any]:

        prompt = f"""
You are PocketSmart AI's jewelry planner.

Return ONLY valid JSON.

Do not return markdown.
Do not return ```json.
Do not add explanations outside JSON.

Budget: INR {data.get("budget", 0)}

Occasion:
{data.get("occasion", "wedding")}

Style:
{data.get("style", "elegant")}

Create practical jewelry recommendations.

Return exactly this structure:

{{
    "recommendations": [
        {{
            "category": "jewelry",
            "title": "string",
            "description": "string",
            "estimated_price": 0,
            "platform": "string",
            "url": "string"
        }}
    ],
    "tips": [
        "string"
    ]
}}

Rules:

1. Keep recommendations within the budget.
2. Use realistic Indian prices.
3. Match the occasion.
4. Match the requested style.
5. Give practical jewelry buying tips.
6. estimated_price must be a number.
7. recommendations must be a JSON array.
8. tips must be a JSON array.
9. Return at least 3 recommendations when possible.
"""

        return self.call(
            prompt,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )


# -------------------------------------------------------------
# NORMALIZE GEMINI RESPONSE
# -------------------------------------------------------------

def normalize_ai(
    data: Any,
    planner: str | None = None,
    budget: float | int | None = None,
) -> dict[str, Any]:

    # Make sure response is a dictionary
    if not isinstance(data, dict):
        data = {}

    # Get recommendations
    recommendations = data.get("recommendations")

    if not isinstance(recommendations, list):
        recommendations = []

    # Clean recommendation items
    cleaned_recommendations = []

    for item in recommendations:

        if not isinstance(item, dict):
            continue

        category = item.get("category", "")
        title = item.get("title", "")
        description = item.get("description", "")
        estimated_price = item.get("estimated_price", 0)
        platform = item.get("platform", "")
        url = item.get("url", "")
        why = item.get("why", "")

        # Make sure price is numeric
        try:
            estimated_price = float(estimated_price)
        except (TypeError, ValueError):
            estimated_price = 0

        cleaned_item = {
            "category": str(category),
            "title": str(title),
            "description": str(description),
            "estimated_price": round(
                estimated_price,
                2,
            ),
            "platform": str(platform),
            "url": str(url),
        }

        # Keep "why" if Gemini provided it
        if why:
            cleaned_item["why"] = str(why)

        cleaned_recommendations.append(
            cleaned_item
        )

    # Get tips
    tips = data.get("tips")

    if not isinstance(tips, list):
        tips = []

    cleaned_tips = []

    for tip in tips:

        if tip is None:
            continue

        cleaned_tips.append(
            str(tip)
        )

    # Update normalized data
    data["recommendations"] = cleaned_recommendations
    data["tips"] = cleaned_tips

    # Add planner
    if planner is not None:
        data["planner"] = planner

    # Add budget
    if budget is not None:
        try:
            data["budget"] = float(budget)
        except (TypeError, ValueError):
            data["budget"] = budget

    # Standard fields
    data.setdefault(
        "currency",
        "INR",
    )

    data.setdefault(
        "allocation",
        {},
    )

    data.setdefault(
        "summary",
        f"AI-generated recommendations for your "
        f"{planner or 'planning'} budget.",
    )

    # Mark as AI generated
    data["ai_generated"] = True

    # Store model name
    data["model"] = settings.gemini_model

    return data


# -------------------------------------------------------------
# GEMINI SERVICE INSTANCE
# -------------------------------------------------------------

gemini_service = GeminiService()