from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AvailabilityRequest,
    BookMeetingRequest,
    PropertyDetailsRequest,
    SearchPropertiesRequest,
    ValidateEmailRequest,
)
from app.services.tool_executor import execute_tool

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.post("/search-properties")
def search_properties(payload: SearchPropertiesRequest):
    try:
        return execute_tool("search_properties", payload.model_dump(exclude_none=True))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Property search failed: {exc}"
        ) from exc


@router.post("/get-property-details")
def get_property_details(payload: PropertyDetailsRequest):
    try:
        return execute_tool("get_property_details", {"property_id": payload.property_id})
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Property lookup failed: {exc}"
        ) from exc


@router.post("/validate-email")
def validate_email_address(payload: ValidateEmailRequest):
    return execute_tool("validate_email", {"email": payload.email})


@router.post("/inventory-overview")
def inventory_overview():
    try:
        return execute_tool("get_inventory_overview", {})
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/check-availability")
def check_availability(payload: AvailabilityRequest):
    try:
        return execute_tool(
            "check_availability",
            {"date": payload.date, "preferred_time": payload.preferred_time},
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
        return execute_tool("book_meeting", payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Booking failed: {exc}"
        ) from exc
