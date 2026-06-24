from pydantic import BaseModel, Field


class AvailabilityRequest(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    preferred_time: str | None = Field(
        default=None, description="Optional preferred time in HH:MM 24-hour IST"
    )


class BookMeetingRequest(BaseModel):
    name: str
    email: str = Field(description="Email as spoken or typed; normalized server-side")
    date: str = Field(description="Date in YYYY-MM-DD format")
    time: str = Field(description="Time in HH:MM 24-hour IST")
    property_id: str | None = None
    property_name: str | None = None


class ValidateEmailRequest(BaseModel):
    email: str = Field(description="Email as the caller said it")


class SearchPropertiesRequest(BaseModel):
    location: str | None = None
    bhk: str | None = None
    property_type: str | None = None
    max_budget_lakhs: float | None = None
    budget: str | None = Field(
        default=None,
        description="Budget as caller said it, e.g. 50 lakh, 1.2 crore",
    )
    query: str | None = None


class PropertyDetailsRequest(BaseModel):
    property_id: str
