"""Nodo Docs — agente especializado en Google Docs."""

from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.google.docs import (
    google_docs_append,
    google_docs_clear,
    google_docs_create,
    google_docs_get,
    google_docs_insert_at,
    google_docs_overwrite,
    google_docs_replace_text,
)

# ── Tools ─────────────────────────────────────────────────────────────────────


@tool
def docs_get(document_id: str) -> str:
    """Obtiene el contenido completo de un Google Doc.

    Args:
        document_id: ID del documento de Google Docs.
    """
    return google_docs_get(document_id)


@tool
def docs_create(title: str, content: str = "", folder_id: Optional[str] = None) -> str:
    """Crea un nuevo Google Doc con contenido inicial.

    Args:
        title: Título del documento.
        content: Contenido inicial del documento (opcional).
        folder_id: ID de la carpeta en Drive donde guardar el doc (opcional).
    """
    return google_docs_create(title, content, folder_id)


@tool
def docs_append(document_id: str, content: str) -> str:
    """Agrega texto al final de un Google Doc existente.

    Args:
        document_id: ID del documento.
        content: Texto a agregar al final.
    """
    return google_docs_append(document_id, content)


@tool
def docs_replace_text(document_id: str, old_text: str, new_text: str) -> str:
    """Reemplaza un texto específico dentro de un Google Doc.

    Args:
        document_id: ID del documento.
        old_text: Texto a buscar y reemplazar.
        new_text: Texto nuevo que reemplazará al anterior.
    """
    return google_docs_replace_text(document_id, old_text, new_text)


@tool
def docs_insert_at(document_id: str, content: str, index: int = 1) -> str:
    """Inserta texto en una posición específica de un Google Doc.

    Args:
        document_id: ID del documento.
        content: Texto a insertar.
        index: Índice de posición (1 = inicio del documento).
    """
    return google_docs_insert_at(document_id, content, index)


@tool
def docs_clear(document_id: str) -> str:
    """Borra todo el contenido de un Google Doc.

    Args:
        document_id: ID del documento a limpiar.
    """
    return google_docs_clear(document_id)


@tool
def docs_overwrite(document_id: str, new_content: str) -> str:
    """Reemplaza todo el contenido de un Google Doc con texto nuevo.

    Args:
        document_id: ID del documento.
        new_content: Nuevo contenido que reemplazará todo el texto actual.
    """
    return google_docs_overwrite(document_id, new_content)


# ── ReAct Agent ───────────────────────────────────────────────────────────────

_DOCS_TOOLS = [docs_get, docs_create, docs_append, docs_replace_text, docs_insert_at, docs_clear, docs_overwrite]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en Google Docs. Gestiona los documentos "
        "del usuario usando las herramientas disponibles.\n\n"
        "- docs_get: Leer el contenido completo de un documento por ID.\n"
        "- docs_create: Crear un documento nuevo con contenido inicial.\n"
        "- docs_append: Agregar texto al final de un documento.\n"
        "- docs_replace_text: Buscar y reemplazar texto dentro de un documento.\n"
        "- docs_insert_at: Insertar texto en una posición específica.\n"
        "- docs_clear: Borrar todo el contenido de un documento.\n"
        "- docs_overwrite: Reemplazar todo el contenido con texto nuevo.\n\n"
        "Responde siempre en el idioma del usuario. Sé conciso y directo."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_DOCS_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def docs_node(state: MessagesState) -> dict:
    """Nodo que procesa tareas de Google Docs usando un agente ReAct interno."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
