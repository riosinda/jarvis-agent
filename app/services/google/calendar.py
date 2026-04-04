from app.core.google_auth import get_calendar_service
from datetime import datetime, timedelta
from typing import Optional


def google_list_events(max_results: int = 10, days_ahead: int = 7) -> str:
    """Lista los próximos eventos del calendario.

    Args:
        max_results: Número máximo de eventos a retornar.
        days_ahead: Cuántos días hacia adelante buscar eventos.

    Returns:
        Lista de eventos con ID, título, fecha y descripción, o descripción del error.
    """
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"
        until = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=until,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        if not events:
            return "No hay eventos próximos."

        output = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            output.append(
                f"ID: {event['id']}\n"
                f"Título: {event.get('summary', 'Sin título')}\n"
                f"Inicio: {start}\n"
                f"Fin: {end}\n"
                f"Descripción: {event.get('description', 'N/A')}\n"
                f"Meet: {event.get('hangoutLink', 'N/A')}\n"
            )

        return "\n---\n".join(output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al listar eventos: {e}"


def google_create_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    attendees: Optional[list[str]] = None,
    add_meet: bool = False,
) -> str:
    """Crea un evento en Google Calendar.

    Args:
        title: Título del evento.
        start_datetime: Fecha y hora de inicio en formato ISO 8601 (ej: '2024-12-01T10:00:00').
        end_datetime: Fecha y hora de fin en formato ISO 8601 (ej: '2024-12-01T11:00:00').
        description: Descripción opcional del evento.
        attendees: Lista de correos de los invitados (ej: ['juan@gmail.com']).
        add_meet: Si es True, agrega un link de Google Meet al evento.

    Returns:
        Mensaje de confirmación con el ID y link del evento, o descripción del error.
    """
    try:
        service = get_calendar_service()

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "America/Mexico_City"},
            "end": {"dateTime": end_datetime, "timeZone": "America/Mexico_City"},
        }

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        if add_meet:
            event["conferenceData"] = {
                "createRequest": {"requestId": f"meet-{datetime.utcnow().timestamp()}"}
            }

        created = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1 if add_meet else 0,
            sendUpdates="all" if attendees else "none",
        ).execute()

        return (
            f"Evento creado correctamente.\n"
            f"ID: {created['id']}\n"
            f"Link: {created.get('htmlLink')}\n"
            f"Meet: {created.get('hangoutLink', 'N/A')}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al crear el evento: {e}"


def google_update_event(
    event_id: str,
    title: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Actualiza un evento existente en Google Calendar.

    Args:
        event_id: ID del evento a actualizar.
        title: Nuevo título del evento (opcional).
        start_datetime: Nueva fecha y hora de inicio en ISO 8601 (opcional).
        end_datetime: Nueva fecha y hora de fin en ISO 8601 (opcional).
        description: Nueva descripción del evento (opcional).

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_calendar_service()

        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        if title:
            event["summary"] = title
        if description:
            event["description"] = description
        if start_datetime:
            event["start"]["dateTime"] = start_datetime
        if end_datetime:
            event["end"]["dateTime"] = end_datetime

        updated = (
            service.events()
            .update(calendarId="primary", eventId=event_id, body=event)
            .execute()
        )

        return f"Evento actualizado correctamente. ID: {updated['id']}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al actualizar el evento: {e}"


def google_delete_event(event_id: str) -> str:
    """Elimina un evento de Google Calendar.

    Args:
        event_id: ID del evento a eliminar.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return f"Evento {event_id} eliminado correctamente."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al eliminar el evento: {e}"


def google_find_free_slots(
    date: str, duration_minutes: int = 60, working_hours: tuple = (9, 18)
) -> str:
    """Encuentra huecos libres en el calendario para una fecha dada.

    Args:
        date: Fecha en formato 'YYYY-MM-DD'.
        duration_minutes: Duración del hueco necesario en minutos.
        working_hours: Tupla con hora inicio y fin del horario laboral (ej: (9, 18)).

    Returns:
        Lista de huecos disponibles o descripción del error.
    """
    try:
        service = get_calendar_service()

        start_of_day = f"{date}T{working_hours[0]:02d}:00:00Z"
        end_of_day = f"{date}T{working_hours[1]:02d}:00:00Z"

        body = {
            "timeMin": start_of_day,
            "timeMax": end_of_day,
            "items": [{"id": "primary"}],
        }

        freebusy = service.freebusy().query(body=body).execute()
        busy_slots = freebusy["calendars"]["primary"]["busy"]

        # Construir lista de huecos libres
        free_slots = []
        current = datetime.fromisoformat(start_of_day.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_of_day.replace("Z", "+00:00"))

        for busy in busy_slots:
            busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
            if (busy_start - current).seconds >= duration_minutes * 60:
                free_slots.append(f"{current.strftime('%H:%M')} - {busy_start.strftime('%H:%M')}")
            current = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))

        if (end - current).seconds >= duration_minutes * 60:
            free_slots.append(f"{current.strftime('%H:%M')} - {end.strftime('%H:%M')}")

        if not free_slots:
            return f"No hay huecos libres de {duration_minutes} minutos el {date}."

        return f"Huecos disponibles el {date}:\n" + "\n".join(free_slots)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al buscar huecos libres: {e}"