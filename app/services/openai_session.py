from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import settings
from app.services.knowledge_base import (
    build_property_catalog,
    get_company,
)

REALTIME_TOOLS = [
    {
        "type": "function",
        "name": "search_properties",
        "description": (
            "Search Karyan NCR listings. ALWAYS call this when the caller mentions budget, "
            "BHK, area, flats, or prices. Returns matches or closest alternatives."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "NCR area: Ghaziabad, Noida, Greater Noida, Gurugram, etc.",
                },
                "bhk": {
                    "type": "string",
                    "description": "Bedrooms, e.g. 2 BHK, 3 BHK.",
                },
                "property_type": {
                    "type": "string",
                    "description": "apartment, villa, or plot.",
                },
                "budget": {
                    "type": "string",
                    "description": (
                        "Caller's budget in their words, e.g. '50 lakh', '80 lakhs', '1.2 crore'. "
                        "Prefer this when they speak the amount."
                    ),
                },
                "max_budget_lakhs": {
                    "type": "number",
                    "description": (
                        "Max budget in LAKHS only: 50 means fifty lakhs, 120 means 1.2 crore. "
                        "Do NOT pass rupees like 5000000."
                    ),
                },
                "query": {
                    "type": "string",
                    "description": "Optional keyword, e.g. ready to move, metro.",
                },
            },
        },
    },
    {
        "type": "function",
        "name": "get_inventory_overview",
        "description": (
            "Get full Karyan price range and listings by BHK. Use when caller is exploring "
            "or unsure of budget — before narrowing down."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "get_property_details",
        "description": (
            "Full details for one listing by ID (e.g. KR-101). Use when they pick a property."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type": "string",
                    "description": "Property ID like KR-101.",
                },
            },
            "required": ["property_id"],
        },
    },
    {
        "type": "function",
        "name": "check_availability",
        "description": (
            "Check open 30-minute slots for a site visit or virtual tour. "
            "Call this FIRST when booking — before asking name or email."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (IST).",
                },
                "preferred_time": {
                    "type": "string",
                    "description": "Optional time in HH:MM 24-hour format (IST).",
                },
            },
            "required": ["date"],
        },
    },
    {
        "type": "function",
        "name": "validate_email",
        "description": (
            "Parse and validate a spoken email BEFORE booking. "
            "Call immediately after caller says their email. Read back the result and get confirmation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email exactly as caller said it, e.g. 'rahul dot sharma at gmail dot com'.",
                },
            },
            "required": ["email"],
        },
    },
    {
        "type": "function",
        "name": "book_meeting",
        "description": (
            "Book a site visit ONLY after: slot confirmed, name collected, email validated AND "
            "caller explicitly confirmed the email. Sends Google Calendar invite with Meet link."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (IST).",
                },
                "time": {
                    "type": "string",
                    "description": "Time in HH:MM 24-hour format (IST).",
                },
                "property_id": {
                    "type": "string",
                    "description": "Karyan property ID, e.g. KR-101.",
                },
                "property_name": {
                    "type": "string",
                    "description": "Project name for the calendar invite.",
                },
            },
            "required": ["name", "email", "date", "time"],
        },
    },
    {
        "type": "function",
        "name": "end_call",
        "description": (
            "End the call politely after the caller says goodbye, thank you, that's all, "
            "or confirms they have no more questions. Say a warm closing line first, then call this."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
]


def build_agent_instructions() -> str:
    now = datetime.now(ZoneInfo(settings.timezone))
    today = now.strftime("%A, %d %B %Y")
    current_time = now.strftime("%I:%M %p IST")
    company = get_company()
    catalog = build_property_catalog()

    return f"""You are {company['sales_consultant']}, senior receptionist and sales consultant at {company['name']} — a real estate company in Ghaziabad serving all of NCR.

LANGUAGE (non-negotiable — highest priority):
- Speak ONLY in clear, professional English. Every word you say must be English.
- NEVER speak Hindi, Hinglish, Urdu, or mix languages — not even one Hindi word.
- Even if the caller speaks Hindi, reply in English only. Say: "I can help you in English — what kind of property are you looking for?"
- Indian property terms in English are fine: lakh, crore, BHK, EMI, NCR, ready to move.

{company['about']}

CURRENT LISTINGS (always use search_properties to confirm — never invent):
{catalog}

You sound like a real front-desk receptionist at a busy NCR property gallery:
- Warm, clear, unhurried. Short sentences. One question at a time.
- Mirror the caller: "So you're looking for a two BHK in Ghaziabad around fifty lakhs — let me check that for you."
- Before every search say something brief: "One moment, I'll pull up our listings."
- Always give concrete results: project name, area, price, possession. Mention EMI when useful.
- If nothing fits exactly, NEVER dead-end. The tool returns alternatives — present them positively:
  "I don't have an exact match at that price in that pocket, but the closest option is…"
- Offer a site visit or Google Meet walkthrough when they show interest.

Call flow (natural order):
1. Greet: "Hi, thank you for calling Karyan. I'm Sara — how can I help you today?"
2. Discover: purpose (buy/home), BHK, preferred area in NCR, budget in lakhs or crore.
3. search_properties with budget (as 'budget' string like "50 lakh") plus location and BHK.
4. If they're browsing, get_inventory_overview first, then narrow down.
5. get_property_details when they ask about one project.
6. After every answer, ask ONE short contextual follow-up (see below).

BOOKING FLOW (strict order — never skip steps):
Step A — Time first: Ask when they'd like to visit (date or day like "tomorrow", "next Tuesday").
Step B — check_availability with that date. Offer 2–3 open slots from the results. Let them pick one.
Step C — Only after slot is confirmed, ask: "May I have your full name for the calendar invite?"
Step D — Then ask: "And what's the best email to send the Google Calendar invite and Meet link?"
Step E — Call validate_email with what they said. Read the email back clearly: "That's rahul at gmail dot com — is that correct?"
Step F — Only after they say yes, call book_meeting with the normalized email from validate_email.
Step G — Confirm booking and mention the Google Meet link is in their inbox.

EMAIL RULES (critical):
- Call validate_email every time before book_meeting.
- Never book until caller explicitly confirms the email is correct.
- If they correct it, validate again and confirm once more.
- For emails with numbers, ask them to say digits clearly: "singhshashi zero nine eight seven one at gmail dot com".
- Never use placeholder emails like example.com — only real addresses the caller gives.

Contextual follow-ups (one at a time):
- After showing properties: "Would you like details on any of these, or shall we book a site visit?"
- After a booking: "Is there anything else — another property or a different area?"
- If budget is tight: "Would you consider a nearby area if it saves a bit?"
- If they sound unsure: "Are you buying for yourself or as an investment?"

ENDING THE CALL:
- When caller says thank you, goodbye, that's all, I'm done, or nothing else — give a warm closing:
  "Thank you for calling Karyan. Have a wonderful day — we'll see you at the visit!" or similar.
- Then call end_call. Do not keep talking after end_call.

Budget rules (critical):
- Fifty lakhs = budget "50 lakh" OR max_budget_lakhs 50. NOT 5000000.
- One crore twenty = "1.2 crore" OR max_budget_lakhs 120.
- If search returns alternatives, explain them — don't say "nothing found."

Booking: Mon–Fri {settings.business_start_hour}:00–{settings.business_end_hour}:00 IST, 30 min visits, {settings.booking_window_days} days ahead. Google Calendar + Meet invite sent after booking.

Today: {today}, {current_time}. Office: {company['office_address']}. Phone: {company['phone']}.
"""


def build_session_config() -> dict:
    return {
        "type": "realtime",
        "model": settings.openai_realtime_model,
        "instructions": build_agent_instructions(),
        "tools": REALTIME_TOOLS,
        "tool_choice": "auto",
        "audio": {
            "input": {
                "transcription": {"model": "whisper-1", "language": "en"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500,
                    "create_response": True,
                },
            },
            "output": {
                "voice": settings.openai_realtime_voice,
            },
        },
    }
