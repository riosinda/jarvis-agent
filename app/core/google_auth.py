import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from app.core.config import settings


def _get_credentials() -> Credentials:
    """Obtain valid Google OAuth2 credentials, refreshing or running the
    authorization flow as needed.  The token is persisted to disk so the
    interactive flow only happens once."""

    creds: Credentials | None = None
    token_path = settings.GOOGLE_TOKEN_PATH
    scopes = settings.GMAIL_SCOPES

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CREDENTIALS_PATH, scopes
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


def get_gmail_service() -> Resource:
    """Return an authorized Gmail API service instance."""
    return build("gmail", "v1", credentials=_get_credentials())


def get_calendar_service() -> Resource:
    """Return an authorized Google Calendar API service instance."""
    return build("calendar", "v3", credentials=_get_credentials())
