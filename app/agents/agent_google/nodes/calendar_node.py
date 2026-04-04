"""Nodo Calendar — agente especializado en Google Calendar."""

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from typing import Optional

from app.agents.select_llm import get_llm
from app.services.google.calendar import (
    google_create_event,
    google_delete_event,
    google_find_free_slots,
    google_list_events,
    google_update_event,
)

# ── Tools ─────────────────────────────────────────────────────────────────────


@tool
def list_events(max_results: int = 10, days_ahead: int = 7) -> str:
    """Lista los próximos eventos del calendario.

    Args:
        max_results: Número máximo de eventos a retornar.
        days_ahead: Cuántos días hacia adelante buscar eventos.
    """
    return google_list_events(max_results, days_ahead)


@tool
def create_event(
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
    """
    return google_create_event(title, start_datetime, end_datetime, description, attendees, add_meet)


@tool
def update_event(
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
    """
    return google_update_event(event_id, title, start_datetime, end_datetime, description)


@tool
def delete_event(event_id: str) -> str:
    """Elimina un evento de Google Calendar.

    Args:
        event_id: ID del evento a eliminar.
    """
    return google_delete_event(event_id)


@tool
def find_free_slots(
    date: str, duration_minutes: int = 60, working_hours: tuple = (9, 18)
) -> str:
    """Encuentra huecos libres en el calendario para una fecha dada.

    Args:
        date: Fecha en formato 'YYYY-MM-DD'.
        duration_minutes: Duración del hueco necesario en minutos.
        working_hours: Tupla con hora inicio y fin del horario laboral (ej: (9, 18)).
    """
    return google_find_free_slots(date, duration_minutes, working_hours)


# ── ReAct Agent ───────────────────────────────────────────────────────────────

_CALENDAR_TOOLS = [list_events, create_event, update_event, delete_event, find_free_slots]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en Google Calendar. Gestiona los eventos "
        "del calendario del usuario usando las herramientas disponibles.\n\n"
        "- list_events: Listar próximos eventos.\n"
        "- create_event: Crear un evento nuevo (con invitados o Meet opcional).\n"
        "- update_event: Actualizar título, fecha o descripción de un evento.\n"
        "- delete_event: Eliminar un evento por ID.\n"
        "- find_free_slots: Encontrar huecos libres en un día dado.\n\n"
        "Responde siempre en el idioma del usuario. Sé conciso y directo."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_CALENDAR_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def calendar_node(state: MessagesState) -> dict:
    """Nodo que procesa tareas de Google Calendar usando un agente ReAct interno."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
