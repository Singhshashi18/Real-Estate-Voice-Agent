from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AvailabilityRequest,
    BookMeetingRequest,
    PropertyDetailsRequest,
    SearchPropertiesRequest,
    ValidateEmailRequest,
)
from app.services import calendar_service, knowledge_base
from app.services.email_utils import validate_email

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.post("/search-properties")
def search_properties(payload: SearchPropertiesRequest):
    try:
        return knowledge_base.search_properties(
            location=payload.location,
            bhk=payload.bhk,
            property_type=payload.property_type,
            max_budget_lakhs=payload.max_budget_lakhs,
            budget=payload.budget,
            query=payload.query,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Property search failed: {exc}"
        ) from exc


@router.post("/get-property-details")
def get_property_details(payload: PropertyDetailsRequest):
    try:
        return knowledge_base.get_property_details(payload.property_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Property lookup failed: {exc}"
        ) from exc


@router.post("/validate-email")
def validate_email_address(payload: ValidateEmailRequest):
    return validate_email(payload.email)


@router.post("/inventory-overview")
def inventory_overview():
    try:
        return knowledge_base.get_inventory_overview()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/check-availability")
def check_availability(payload: AvailabilityRequest):
    try:
        return calendar_service.check_availability(
            payload.date, payload.preferred_time
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Calendar check failed: {exc}"
        ) from exc


@router.post("/book-meeting")
def book_meeting(payload: BookMeetingRequest):
    try:
        return calendar_service.book_meeting(
            payload.name,
            payload.email,
            payload.date,
            payload.time,
            property_id=payload.property_id,
            property_name=payload.property_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Booking failed: {exc}"
        ) from exc
