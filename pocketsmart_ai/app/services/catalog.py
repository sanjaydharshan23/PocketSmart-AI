from urllib.parse import quote_plus

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/search?q={q}",
    "OYO": "https://www.oyorooms.com/search?location={q}",
}

def search_url(platform: str, query: str) -> str:
    template = PLATFORMS.get(platform, PLATFORMS["Amazon"])
    return template.format(q=quote_plus(query))

def fallback_home(budget: float, style: str, rooms: list[str], quantities: dict[str,int]):
    base = max(500, budget / max(3, len(rooms) or 3))
    products = [
        ("Lighting", "Warm LED ceiling light", base * .35, "Amazon", "functional lighting with warm ambience"),
        ("Furniture", f"{style.title()} compact side table", base * .65, "IKEA", "space-efficient piece matching the selected style"),
        ("Decor", "Minimal wall art set", base * .25, "Flipkart", "low-cost visual upgrade"),
        ("Cooling", "Energy-efficient ceiling fan", base * .9, "Amazon", "practical comfort within the plan"),
    ]
    return products

def fallback_party(budget: float, guests: int, event_type: str, city: str):
    return [
        ("Catering", f"{event_type.title()} buffet package for {guests}", budget*.45, "Swiggy", "keeps food as the largest event allocation"),
        ("Venue", f"Event venue options in {city or 'your city'}", budget*.30, "OYO", "room for venue and basic guest needs"),
        ("Decor", "Theme decoration package", budget*.15, "Amazon", "simple decor that fits the event theme"),
        ("Entertainment", "Music / games / activity budget", budget*.10, "Zomato", "reserved amount for event extras"),
    ]

def fallback_jewelry(budget: float, occasion: str, style: str):
    return [
        ("Earrings", f"{style.title()} earrings for {occasion}", budget*.28, "Amazon", "easy-to-match statement or minimal option"),
        ("Necklace", f"{style.title()} necklace set", budget*.42, "Flipkart", "balances the outfit without consuming the full budget"),
        ("Bangles", "Coordinated bangle set", budget*.18, "Amazon", "adds detail while keeping spend controlled"),
        ("Accessories", "Matching hair/accessory accents", budget*.08, "Flipkart", "small finishing touches"),
    ]
