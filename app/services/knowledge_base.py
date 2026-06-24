from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.config import settings

KB_PATH = settings.root_dir / "data" / "karyan_knowledge_base.json"

_cache: dict[str, Any] | None = None

# Budget flex: show options slightly above stated budget (real receptionist behaviour)
BUDGET_FLEX_PERCENT = 0.15  # 15% above stated budget still shown as "closest match"

LOCATION_ALIASES: dict[str, list[str]] = {
    "ghaziabad": [
        "ghaziabad",
        "gzb",
        "raj nagar",
        "crossings republik",
        "sikandra",
        "nh-58",
        "vaishali",
        "indirapuram",
    ],
    "noida": ["noida", "sector 150", "noida expressway"],
    "greater noida": ["greater noida", "noida west", "noida extension"],
    "gurugram": ["gurugram", "gurgaon", "dwarka expressway", "golf course"],
    "faridabad": ["faridabad"],
    "delhi": ["delhi", "delhi ncr", "ncr"],
}


def load_knowledge_base() -> dict[str, Any]:
    global _cache
    if _cache is not None:
        return _cache
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base not found at {KB_PATH}")
    _cache = json.loads(KB_PATH.read_text(encoding="utf-8"))
    return _cache


def get_company() -> dict[str, Any]:
    return load_knowledge_base()["company"]


def get_faqs() -> list[dict[str, str]]:
    return load_knowledge_base().get("faqs", [])


def parse_budget_to_lakhs(value: str | float | int | None) -> float | None:
    """Parse Indian budget phrases into lakhs (50 lakh -> 50, 1.2 cr -> 120)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        num = float(value)
        # Model sometimes passes rupees (5200000) instead of lakhs
        if num >= 100_000:
            return num / 100_000
        return num

    text = str(value).lower().strip()
    if not text:
        return None

    text = text.replace("₹", "").replace("rs", "").replace("inr", "").strip()
    text = re.sub(r"\s+", " ", text)

    crore_match = re.search(r"([\d.]+)\s*(crore|cr|crores)", text)
    if crore_match:
        return float(crore_match.group(1)) * 100

    lakh_match = re.search(r"([\d.]+)\s*(lakh|lakhs|lac|lacs|l)", text)
    if lakh_match:
        return float(lakh_match.group(1))

    # Plain number with "thousand" / k
    if "thousand" in text or re.search(r"\d+k\b", text):
        return None

    digits = re.search(r"([\d.]+)", text)
    if not digits:
        return None

    num = float(digits.group(1))
    if num >= 100_000:
        return num / 100_000
    if num >= 1000 and "lakh" not in text and "crore" not in text:
        # Ambiguous large number — treat as rupees
        return num / 100_000
    return num


def _normalize_bhk(bhk: str | None) -> str | None:
    if not bhk:
        return None
    match = re.search(r"(\d+)", bhk)
    return match.group(1) if match else bhk.lower().replace(" ", "")


def _location_matches(prop_location: str, user_location: str) -> bool:
    loc = prop_location.lower()
    needle = user_location.lower().strip()
    if needle in loc or loc in needle:
        return True
    for _region, aliases in LOCATION_ALIASES.items():
        if any(a in needle for a in aliases) or needle in _region:
            if any(a in loc for a in aliases) or _region in loc:
                return True
    return False


def _property_summary(prop: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": prop["id"],
        "name": prop["name"],
        "type": prop["type"],
        "location": prop["location"],
        "bhk": prop["bhk"],
        "size_sqft": prop["size_sqft"],
        "price_inr": prop["price_inr"],
        "price_display": prop["price_display"],
        "emi_from": prop.get("emi_from"),
        "status": prop["status"],
        "possession": prop["possession"],
        "highlights": prop.get("highlights", [])[:2],
    }


def _format_listing_line(prop: dict[str, Any]) -> str:
    return (
        f"{prop['id']}: {prop['bhk']} {prop['type']} in {prop['location']} — "
        f"{prop['price_display']}, EMI from {prop.get('emi_from', 'on request')}, {prop['possession']}"
    )


def _filter_properties(
    properties: list[dict[str, Any]],
    *,
    location: str | None,
    bhk: str | None,
    property_type: str | None,
    max_budget_lakhs: float | None,
    query: str | None,
) -> list[dict[str, Any]]:
    results = list(properties)

    if location:
        results = [p for p in results if _location_matches(p["location"], location)]

    if bhk:
        bhk_num = _normalize_bhk(bhk)
        if bhk_num:
            results = [
                p
                for p in results
                if bhk_num in _normalize_bhk(p["bhk"]) or bhk_num in p["bhk"]
            ]

    if property_type:
        needle = property_type.lower().replace("flat", "apartment")
        results = [p for p in results if needle in p["type"].lower() or needle in p["name"].lower()]

    if max_budget_lakhs is not None:
        cap = max_budget_lakhs * 100_000
        flex_cap = cap * (1 + BUDGET_FLEX_PERCENT)
        in_budget = [p for p in results if p["price_inr"] <= cap]
        if in_budget:
            results = in_budget
        else:
            # Slightly above budget — still show closest options
            near = [p for p in results if p["price_inr"] <= flex_cap]
            results = near if near else results

    if query:
        needle = query.lower()
        results = [
            p
            for p in results
            if needle in p["name"].lower()
            or needle in p["location"].lower()
            or needle in p["bhk"].lower()
            or any(needle in h.lower() for h in p.get("highlights", []))
        ]

    return sorted(results, key=lambda p: p["price_inr"])


def _nearest_alternatives(
    properties: list[dict[str, Any]],
    *,
    max_budget_lakhs: float | None,
    bhk: str | None,
    location: str | None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    pool = list(properties)
    if bhk:
        bhk_num = _normalize_bhk(bhk)
        if bhk_num:
            pool = [p for p in pool if bhk_num in (_normalize_bhk(p["bhk"]) or "")]
    if location:
        pool = [p for p in pool if _location_matches(p["location"], location)] or list(
            properties
        )

    if max_budget_lakhs is not None:
        cap = max_budget_lakhs * 100_000
        # Closest above budget, then below
        above = sorted(
            [p for p in pool if p["price_inr"] > cap],
            key=lambda p: p["price_inr"],
        )
        below = sorted(
            [p for p in pool if p["price_inr"] <= cap],
            key=lambda p: p["price_inr"],
            reverse=True,
        )
        combined = below[:2] + above[:2]
        return combined[:limit]

    return sorted(pool, key=lambda p: p["price_inr"])[:limit]


def get_property_details(property_id: str) -> dict[str, Any]:
    kb = load_knowledge_base()
    needle = property_id.strip().upper()
    prop = next((p for p in kb["properties"] if p["id"].upper() == needle), None)
    if not prop:
        return {
            "found": False,
            "message": f"I don't have a listing with ID {property_id}. Let me search by your budget and area instead.",
        }
    return {
        "found": True,
        "message": (
            f"{prop['name']} ({prop['id']}): {prop['bhk']} {prop['type']} in {prop['location']}. "
            f"Price {prop['price_display']}, {prop['size_sqft']} sqft, {prop['status']}, "
            f"possession {prop['possession']}. Highlights: {', '.join(prop.get('highlights', [])[:3])}."
        ),
        "property": prop,
    }


def search_properties(
    location: str | None = None,
    bhk: str | None = None,
    property_type: str | None = None,
    max_budget_lakhs: float | None = None,
    budget: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    kb = load_knowledge_base()
    available = [
        p
        for p in kb["properties"]
        if p["status"] in ("available", "few_units_left")
    ]

    # Merge budget string + numeric budget
    parsed_budget = parse_budget_to_lakhs(budget) or parse_budget_to_lakhs(max_budget_lakhs)
    if parsed_budget is not None:
        max_budget_lakhs = parsed_budget

    results = _filter_properties(
        available,
        location=location,
        bhk=bhk,
        property_type=property_type,
        max_budget_lakhs=max_budget_lakhs,
        query=query,
    )

    # Same filters without budget — for "slightly above" suggestions
    unbudgeted = _filter_properties(
        available,
        location=location,
        bhk=bhk,
        property_type=property_type,
        max_budget_lakhs=None,
        query=query,
    )

    strict_budget = max_budget_lakhs
    if strict_budget is not None:
        cap = strict_budget * 100_000
        exact_budget = [p for p in results if p["price_inr"] <= cap]
    else:
        exact_budget = results

    if exact_budget:
        summaries = [_property_summary(p) for p in exact_budget[:5]]
        lines = [_format_listing_line(p) for p in exact_budget[:5]]

        # Mention slightly-above-budget options a real receptionist would flag
        near_above: list[dict[str, Any]] = []
        if strict_budget is not None:
            cap = strict_budget * 100_000
            flex_cap = cap * (1 + BUDGET_FLEX_PERCENT)
            matched_ids = {p["id"] for p in exact_budget}
            near_above = sorted(
                [
                    p
                    for p in unbudgeted
                    if p["id"] not in matched_ids
                    and cap < p["price_inr"] <= flex_cap
                ],
                key=lambda p: p["price_inr"],
            )[:2]

        more = f" Plus {len(exact_budget) - 5} more." if len(exact_budget) > 5 else ""
        budget_note = (
            f" within ₹{strict_budget:.0f} Lakh budget"
            if strict_budget is not None
            else ""
        )
        near_note = ""
        if near_above:
            near_lines = [_format_listing_line(p) for p in near_above]
            near_note = (
                " Just above your budget: " + " | ".join(near_lines) + "."
            )
        return {
            "count": len(exact_budget),
            "matched_budget": True,
            "message": (
                f"Found {len(exact_budget)} option(s){budget_note}: "
                + " | ".join(lines)
                + more
                + near_note
                + " Offer to share details or book a site visit."
            ),
            "properties": summaries,
            "alternatives": [_property_summary(p) for p in near_above] if near_above else [],
        }

    # No exact match — receptionist-style alternatives
    alternatives = _nearest_alternatives(
        available,
        max_budget_lakhs=max_budget_lakhs,
        bhk=bhk,
        location=location,
        limit=4,
    )

    if not alternatives:
        cheapest = sorted(available, key=lambda p: p["price_inr"])[:3]
        lines = [_format_listing_line(p) for p in cheapest]
        return {
            "count": 0,
            "matched_budget": False,
            "message": (
                "No exact match for those filters. Our most affordable NCR listings right now: "
                + " | ".join(lines)
                + ". Ask if they'd like details or a slightly different area or BHK."
            ),
            "properties": [_property_summary(p) for p in cheapest],
            "alternatives": [_property_summary(p) for p in cheapest],
        }

    alt_lines = [_format_listing_line(p) for p in alternatives]
    budget_phrase = (
        f"Nothing exact under ₹{strict_budget:.0f} Lakh"
        if strict_budget is not None
        else "No exact match"
    )
    return {
        "count": 0,
        "matched_budget": False,
        "message": (
            f"{budget_phrase} with those filters, but here are the closest Karyan options: "
            + " | ".join(alt_lines)
            + ". Explain these warmly and ask if they'd stretch budget slightly or prefer another area."
        ),
        "properties": [],
        "alternatives": [_property_summary(p) for p in alternatives],
    }


def get_inventory_overview() -> dict[str, Any]:
    kb = load_knowledge_base()
    available = sorted(
        [p for p in kb["properties"] if p["status"] in ("available", "few_units_left")],
        key=lambda p: p["price_inr"],
    )
    by_bhk: dict[str, list[str]] = {}
    for p in available:
        key = p["bhk"]
        by_bhk.setdefault(key, []).append(
            f"{p['location']} from {p['price_display']} ({p['id']})"
        )

    lines = [
        f"{bhk}: " + "; ".join(items[:3])
        for bhk, items in sorted(by_bhk.items())
    ]
    cheapest = available[0]
    priciest = available[-1]
    return {
        "message": (
            f"Karyan NCR inventory: {len(available)} listings from {cheapest['price_display']} "
            f"({cheapest['location']}) up to {priciest['price_display']} ({priciest['location']}). "
            + " | ".join(lines)
        ),
        "price_range": {
            "min_display": cheapest["price_display"],
            "max_display": priciest["price_display"],
        },
        "listings": [_property_summary(p) for p in available],
    }


def build_property_catalog() -> str:
    kb = load_knowledge_base()
    lines = []
    for p in sorted(kb["properties"], key=lambda x: x["price_inr"]):
        lines.append(
            f"- {p['id']}: {p['bhk']} {p['type']}, {p['location']}, {p['price_display']}, {p['possession']}"
        )
    return "\n".join(lines)


def build_knowledge_summary() -> str:
    kb = load_knowledge_base()
    company = kb["company"]
    available = [p for p in kb["properties"] if p["status"] in ("available", "few_units_left")]
    cheapest = min(available, key=lambda p: p["price_inr"])
    return (
        f"{company['name']} — Ghaziabad HQ, full NCR. "
        f"{len(available)} listings, from {cheapest['price_display']}. "
        f"Areas: {', '.join(company.get('service_areas', []))}."
    )
