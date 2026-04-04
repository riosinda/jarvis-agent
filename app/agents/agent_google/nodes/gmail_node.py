"""Nodo Gmail — agente especializado en correos electrónicos."""

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.google.gmail import (
    google_archive_email,
    google_list_emails,
    google_mark_as_read,
    google_read_email,
    google_reply_email,
    google_send_email,
)

# ── Tools ─────────────────────────────────────────────────────────────────────


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Envía un correo electrónico a través de Gmail.

    Args:
        to: Dirección de correo del destinatario.
        subject: Asunto del correo.
        body: Cuerpo del correo en texto plano.
    """
    return google_send_email(to, subject, body)


@tool
def list_emails(max_results: int = 10, query: str = "") -> str:
    """Lista los correos de la bandeja de entrada.

    Args:
        max_results: Número máximo de correos a retornar.
        query: Filtro de búsqueda (ej: 'is:unread', 'from:juan@gmail.com').
    """
    return google_list_emails(max_results, query)


@tool
def read_email(message_id: str) -> str:
    """Lee el contenido completo de un correo por su ID.

    Args:
        message_id: ID del correo a leer.
    """
    return google_read_email(message_id)


@tool
def reply_email(message_id: str, body: str) -> str:
    """Responde a un correo existente manteniendo el hilo.

    Args:
        message_id: ID del correo al que se responde.
        body: Cuerpo de la respuesta.
    """
    return google_reply_email(message_id, body)


@tool
def mark_as_read(message_id: str) -> str:
    """Marca un correo como leído.

    Args:
        message_id: ID del correo.
    """
    return google_mark_as_read(message_id)


@tool
def archive_email(message_id: str) -> str:
    """Archiva un correo (lo quita de la bandeja de entrada).

    Args:
        message_id: ID del correo.
    """
    return google_archive_email(message_id)


# ── ReAct Agent ───────────────────────────────────────────────────────────────

_GMAIL_TOOLS = [send_email, list_emails, read_email, reply_email, mark_as_read, archive_email]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en Gmail. Gestiona el correo electrónico "
        "del usuario usando las herramientas disponibles.\n\n"
        "- send_email: Enviar un correo nuevo.\n"
        "- list_emails: Listar correos de la bandeja de entrada.\n"
        "- read_email: Leer el contenido de un correo por ID.\n"
        "- reply_email: Responder a un correo manteniendo el hilo.\n"
        "- mark_as_read: Marcar un correo como leído.\n"
        "- archive_email: Archivar un correo.\n\n"
        "Responde siempre en el idioma del usuario. Sé conciso y directo."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_GMAIL_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def gmail_node(state: MessagesState) -> dict:
    """Nodo que procesa tareas de Gmail usando un agente ReAct interno."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
