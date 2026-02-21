import base64
import requests
from email.mime.text import MIMEText
from datetime import datetime

from langchain_core.tools import tool

from app.core.config import settings
from app.core.google_auth import get_gmail_service, get_calendar_service


# ── Gmail Tool ───────────────────────────────────────────────────────────────


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Envía un correo electrónico a través de Gmail.

    Args:
        to: Dirección de correo del destinatario.
        subject: Asunto del correo.
        body: Cuerpo del correo en texto plano.

    Returns:
        Mensaje de confirmación con el ID del correo enviado, o una descripción del error.
    """
    try:
        service = get_gmail_service()
        sender = settings.GMAIL_SENDER_EMAIL

        message = MIMEText(body)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return f"Email enviado correctamente. Message ID: {sent['id']}"
    except Exception as e:
        return f"Error al enviar el email: {e}"


# ── Google Calendar Tool ─────────────────────────────────────────────────────


@tool
def create_calendar_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    location: str = "",
    timezone: str = "America/Mexico_City",
) -> str:
    """Crea un nuevo evento en Google Calendar.

    Args:
        summary: Título del evento.
        start_datetime: Fecha y hora de inicio en formato ISO 8601 (ej. '2026-03-01T10:00:00').
        end_datetime: Fecha y hora de fin en formato ISO 8601 (ej. '2026-03-01T11:00:00').
        description: Descripción o notas opcionales del evento.
        location: Ubicación opcional del evento.
        timezone: Zona horaria del evento (por defecto: America/Mexico_City).

    Returns:
        Mensaje de confirmación con el link del evento creado, o una descripción del error.
    """
    try:
        # Validate datetime format
        datetime.fromisoformat(start_datetime)
        datetime.fromisoformat(end_datetime)

        service = get_calendar_service()

        event_body = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_datetime,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": timezone,
            },
        }

        event = (
            service.events()
            .insert(calendarId="primary", body=event_body)
            .execute()
        )
        return (
            f"Evento creado correctamente: {event.get('summary')} "
            f"— Link: {event.get('htmlLink')}"
        )
    except ValueError as e:
        return f"Formato de fecha inválido: {e}. Usa formato ISO 8601 (ej. '2026-03-01T10:00:00')."
    except Exception as e:
        return f"Error al crear el evento: {e}"


# ── Date & Time Tool ─────────────────────────────────────────────────────────


@tool
def get_current_datetime(timezone: str = "America/Mexico_City") -> str:
    """Obtiene la fecha y hora actuales para una zona horaria dada.

    Args:
        timezone: Identificador de zona horaria válido (ej. 'America/Mexico_City', 'US/Eastern', 'Europe/London').

    Returns:
        Texto legible con la fecha, hora, día de la semana y zona horaria actuales.
    """
    try:
        response = requests.get(
            f"https://timeapi.io/api/time/current/zone?timeZone={timezone}",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        return (
            f"Fecha: {data['date']}\n"
            f"Hora: {data['time']}\n"
            f"Día: {data['dayOfWeek']}\n"
            f"Zona horaria: {data['timeZone']}"
        )
    except requests.exceptions.HTTPError:
        return (
            f"Timezone '{timezone}' no válida. "
            "Usa un identificador como 'America/Mexico_City', 'US/Eastern', 'Europe/Madrid', etc."
        )
    except Exception as e:
        return f"Error al obtener la fecha/hora: {e}"


# ── Export ────────────────────────────────────────────────────────────────────

agent_tools = [send_email, create_calendar_event, get_current_datetime]
