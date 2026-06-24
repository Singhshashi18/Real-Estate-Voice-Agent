from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.config import settings
from app.services.booking_email import send_booking_confirmation
from app.services.email_utils import normalize_spoken_email, validate_email as check_email
from app.services.google_auth import get_calendar_service, get_organizer_email

TZ = ZoneInfo(settings.timezone)
SLOT_MINUTES = settings.meeting_duration_minutes


def _now_ist() -> datetime:
    return datetime.now(TZ)


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _parse_time(value: str) -> time:
    parts = value.strip().split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    return time(hour, minute)


def _to_datetime(day: date, clock: time) -> datetime:
    return datetime.combine(day, clock, tzinfo=TZ)


def _is_business_day(day: date) -> bool:
    return day.weekday() < 5


def _booking_window() -> tuple[datetime, datetime]:
    now = _now_ist()
    end = now + timedelta(days=settings.booking_window_days)
    return now, end


def _validate_booking_datetime(start: datetime) -> str | None:
    now, window_end = _booking_window()

    if start < now:
        return "That time is in the past. Please choose a future time."

    if start > window_end:
        return (
            f"Bookings are only available up to {settings.booking_window_days} days ahead."
        )

    if not _is_business_day(start.date()):
        return "Meetings can only be booked Monday through Friday."

    day_start = _to_datetime(start.date(), time(settings.business_start_hour, 0))
    day_end = _to_datetime(start.date(), time(settings.business_end_hour, 0))
    slot_end = start + timedelta(minutes=SLOT_MINUTES)

    if start < day_start or slot_end > day_end:
        return (
            f"Business hours are {settings.business_start_hour}:00 to "
            f"{settings.business_end_hour}:00 IST, Monday to Friday."
        )

    return None


def _busy_intervals(range_start: datetime, range_end: datetime) -> list[tuple[datetime, datetime]]:
    service = get_calendar_service()
    body = {
        "timeMin": range_start.isoformat(),
        "timeMax": range_end.isoformat(),
        "timeZone": settings.timezone,
        "items": [{"id": settings.google_calendar_id}],
    }
    result = service.freebusy().query(body=body).execute()
    busy = result["calendars"][settings.google_calendar_id].get("busy", [])
    intervals: list[tuple[datetime, datetime]] = []
    for block in busy:
        start = datetime.fromisoformat(block["start"].replace("Z", "+00:00")).astimezone(TZ)
        end = datetime.fromisoformat(block["end"].replace("Z", "+00:00")).astimezone(TZ)
        intervals.append((start, end))
    return intervals


def _overlaps(start: datetime, end: datetime, busy: list[tuple[datetime, datetime]]) -> bool:
    for busy_start, busy_end in busy:
        if start < busy_end and end > busy_start:
            return True
    return False


def _iter_slot_starts(day: date) -> list[datetime]:
    if not _is_business_day(day):
        return []

    start = _to_datetime(day, time(settings.business_start_hour, 0))
    last_start = _to_datetime(day, time(settings.business_end_hour, 0)) - timedelta(
        minutes=SLOT_MINUTES
    )
    slots: list[datetime] = []
    current = start
    while current <= last_start:
        slots.append(current)
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


def _format_slot(dt: datetime) -> str:
    return dt.strftime("%A, %d %B %Y at %I:%M %p IST")


def check_availability(date_str: str, preferred_time: str | None = None) -> dict:
    day = _parse_date(date_str)
    now, window_end = _booking_window()

    if day < now.date():
        return {"available": False, "message": "That date is in the past."}

    if day > window_end.date():
        return {
            "available": False,
            "message": f"Bookings are only available up to {settings.booking_window_days} days ahead.",
        }

    if not _is_business_day(day):
        return {
            "available": False,
            "message": "Meetings can only be booked Monday through Friday.",
        }

    day_start = _to_datetime(day, time(settings.business_start_hour, 0))
    day_end = _to_datetime(day, time(settings.business_end_hour, 0))
    busy = _busy_intervals(day_start, day_end)

    if preferred_time:
        start = _to_datetime(day, _parse_time(preferred_time))
        validation_error = _validate_booking_datetime(start)
        if validation_error:
            return {"available": False, "message": validation_error}

        end = start + timedelta(minutes=SLOT_MINUTES)
        is_free = not _overlaps(start, end, busy)
        if is_free:
            return {
                "available": True,
                "message": f"{_format_slot(start)} is available.",
                "slot": start.isoformat(),
            }

        alternatives = get_available_slots(date_str, limit=3)
        alt_text = ", ".join(alternatives["slots"]) if alternatives["slots"] else "none"
        return {
            "available": False,
            "message": (
                f"{_format_slot(start)} is not available. "
                f"Here are some alternatives: {alt_text}."
            ),
            "alternatives": alternatives["slots"],
        }

    open_slots = []
    for slot_start in _iter_slot_starts(day):
        if slot_start < now:
            continue
        slot_end = slot_start + timedelta(minutes=SLOT_MINUTES)
        if not _overlaps(slot_start, slot_end, busy):
            open_slots.append(_format_slot(slot_start))

    if not open_slots:
        return {
            "available": False,
            "message": f"No open 30-minute slots on {day.isoformat()}.",
            "slots": [],
        }

    preview = ", ".join(open_slots[:5])
    more = f" and {len(open_slots) - 5} more" if len(open_slots) > 5 else ""
    return {
        "available": True,
        "message": f"Available slots on {day.isoformat()}: {preview}{more}.",
        "slots": open_slots,
    }


def get_available_slots(date_str: str, limit: int = 5) -> dict:
    result = check_availability(date_str)
    slots = result.get("slots", [])
    return {"slots": slots[:limit]}


def book_meeting(
    name: str,
    email: str,
    date_str: str,
    time_str: str,
    property_id: str | None = None,
    property_name: str | None = None,
) -> dict:
    name = name.strip()
    email = normalize_spoken_email(email)
    email_check = check_email(email)
    if not email_check["valid"]:
        return {"success": False, "message": email_check["message"]}

    email = email_check["normalized"]

    day = _parse_date(date_str)
    start = _to_datetime(day, _parse_time(time_str))
    validation_error = _validate_booking_datetime(start)
    if validation_error:
        return {"success": False, "message": validation_error}

    end = start + timedelta(minutes=SLOT_MINUTES)
    busy = _busy_intervals(start, end)
    if _overlaps(start, end, busy):
        alternatives = get_available_slots(date_str, limit=3)
        alt_text = ", ".join(alternatives["slots"]) if alternatives["slots"] else "none"
        return {
            "success": False,
            "message": (
                f"That slot is no longer available. Alternatives: {alt_text}."
            ),
        }

    property_label = property_name or "Karyan property"
    if property_id:
        property_label = f"{property_label} ({property_id})"

    organizer_email = get_organizer_email()
    same_account = (
        organizer_email is not None and email.lower() == organizer_email.lower()
    )

    service = get_calendar_service()
    event: dict = {
        "summary": f"Karyan site visit — {property_label} with {name}",
        "description": (
            f"30-minute property visit / virtual tour booked via {settings.company_name}.\n"
            f"Guest: {name} ({email})\n"
            f"Property: {property_label}\n"
            f"Sales consultant: {settings.organizer_name}"
        ),
        "start": {"dateTime": start.isoformat(), "timeZone": settings.timezone},
        "end": {"dateTime": end.isoformat(), "timeZone": settings.timezone},
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 30},
            ],
        },
    }

    event["attendees"] = [{"email": email, "displayName": name}]
    send_updates = "all"

    created = (
        service.events()
        .insert(
            calendarId=settings.google_calendar_id,
            body=event,
            conferenceDataVersion=1,
            sendUpdates=send_updates,
        )
        .execute()
    )

    meet_link = created.get("hangoutLink") or ""
    if not meet_link:
        entry_points = created.get("conferenceData", {}).get("entryPoints", [])
        for ep in entry_points:
            if ep.get("entryPointType") == "video":
                meet_link = ep.get("uri", "")
                break

    email_result = send_booking_confirmation(
        guest_name=name,
        guest_email=email,
        property_label=property_label,
        slot_label=_format_slot(start),
        meet_link=meet_link,
    )

    if email_result["sent"]:
        delivery_note = f"A confirmation email and calendar invite were sent to {email}."
    elif same_account:
        delivery_note = (
            f"The visit is on your Google Calendar with the Meet link. "
            f"{email_result['message']}"
        )
    else:
        delivery_note = (
            f"Calendar invite sent to {email}. {email_result['message']}"
        )

    return {
        "success": True,
        "message": (
            f"Booked a site visit for {property_label} on {_format_slot(start)} with {name}. "
            f"{delivery_note} "
            f"Meet link: {meet_link or 'open the event in Google Calendar'}."
        ),
        "event_id": created.get("id"),
        "meet_link": meet_link,
        "email_sent_to": email,
        "confirmation_email_sent": email_result["sent"],
        "same_calendar_account": same_account,
        "start": start.isoformat(),
    }
