from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent

 
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    root_dir: Path = ROOT_DIR
    openai_api_key: str
    openai_realtime_model: str = "gpt-realtime"
    openai_realtime_voice: str = "shimmer"
    organizer_name: str = "Organizer"
    company_name: str = "Company"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    frontend_url: str = "http://127.0.0.1:3000"
    api_public_url: str = "http://127.0.0.1:8000"

    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    x_client_id: str = ""
    x_client_secret: str = ""

    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001,"
        "http://localhost:3002,http://127.0.0.1:3002"
    )

    google_credentials_path: Path = ROOT_DIR / "credentials.json"
    google_token_path: Path = ROOT_DIR / "token.json"
    google_calendar_id: str = "primary"
    # Cloud deploy: paste contents of token.json as one-line JSON string
    google_token_json: str = ""

    timezone: str = "Asia/Kolkata"
    meeting_duration_minutes: int = 30
    booking_window_days: int = 14
    business_start_hour: int = 9
    business_end_hour: int = 21  # last slot starts at 20:30

    # Twilio (phone)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # ElevenLabs — agent/voice configured in dashboard; API key optional (voices helper)
    elevenlabs_api_key: str = ""
    elevenlabs_outbound_agent_id: str = ""
    elevenlabs_phone_number_id: str = ""

    # Protect /api/telephony/tools/* (set in ElevenLabs tool headers as Bearer token)
    telephony_webhook_secret: str = ""
    elevenlabs_webhook_secret: str = ""  # optional ElevenLabs-Signature validation

    # HubSpot CRM lead source (private app access token)
    hubspot_access_token: str = ""
    # When leads sync from a CRM source, immediately start an outbound call
    outbound_auto_call: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def load_google_oauth_from_credentials(self):
        if self.google_oauth_client_id:
            return self
        if not self.google_credentials_path.exists():
            return self
        import json

        data = json.loads(self.google_credentials_path.read_text(encoding="utf-8"))
        block = data.get("web") or data.get("installed")
        if not block:
            return self
        object.__setattr__(self, "google_oauth_client_id", block.get("client_id", ""))
        object.__setattr__(
            self, "google_oauth_client_secret", block.get("client_secret", "")
        )
        return self


settings = Settings()
