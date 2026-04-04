"""Nodo Drive — agente especializado en Google Drive."""

from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.google.drive import (
    google_create_document,
    google_delete_file,
    google_list_files,
    google_read_file,
    google_search_files,
    google_share_file,
    google_upload_file,
)

# ── Tools ─────────────────────────────────────────────────────────────────────


@tool
def list_files(
    max_results: int = 10,
    query: str = "",
    folder_id: Optional[str] = None,
) -> str:
    """Lista archivos en Google Drive.

    Args:
        max_results: Número máximo de archivos a retornar.
        query: Filtro de búsqueda (ej: "name contains 'reporte'").
        folder_id: ID de la carpeta donde buscar (opcional).
    """
    return google_list_files(max_results, query, folder_id)


@tool
def search_files(search_term: str, max_results: int = 10) -> str:
    """Busca archivos en Google Drive por nombre o contenido.

    Args:
        search_term: Término de búsqueda.
        max_results: Número máximo de resultados.
    """
    return google_search_files(search_term, max_results)


@tool
def read_file(file_id: str) -> str:
    """Lee el contenido de un archivo de Google Drive.
    Soporta Google Docs, Sheets y archivos de texto plano.

    Args:
        file_id: ID del archivo a leer.
    """
    return google_read_file(file_id)


@tool
def create_document(title: str, content: str = "", folder_id: Optional[str] = None) -> str:
    """Crea un nuevo Google Doc en Drive.

    Args:
        title: Título del documento.
        content: Contenido inicial del documento (opcional).
        folder_id: ID de la carpeta donde crear el documento (opcional).
    """
    return google_create_document(title, content, folder_id)


@tool
def upload_file(
    file_path: str,
    file_name: str,
    mime_type: str = "application/octet-stream",
    folder_id: Optional[str] = None,
) -> str:
    """Sube un archivo local a Google Drive.

    Args:
        file_path: Ruta local del archivo a subir.
        file_name: Nombre del archivo en Drive.
        mime_type: Tipo MIME del archivo (ej: 'application/pdf', 'image/png').
        folder_id: ID de la carpeta destino (opcional).
    """
    return google_upload_file(file_path, file_name, mime_type, folder_id)


@tool
def delete_file(file_id: str) -> str:
    """Elimina un archivo de Google Drive (lo mueve a la papelera).

    Args:
        file_id: ID del archivo a eliminar.
    """
    return google_delete_file(file_id)


@tool
def share_file(file_id: str, email: str, role: str = "reader") -> str:
    """Comparte un archivo de Google Drive con un usuario.

    Args:
        file_id: ID del archivo a compartir.
        email: Correo del usuario con quien compartir.
        role: Nivel de acceso ('reader', 'commenter', 'writer').
    """
    return google_share_file(file_id, email, role)


# ── ReAct Agent ───────────────────────────────────────────────────────────────

_DRIVE_TOOLS = [list_files, search_files, read_file, create_document, upload_file, delete_file, share_file]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en Google Drive. Gestiona los archivos "
        "del usuario usando las herramientas disponibles.\n\n"
        "- list_files: Listar archivos (con filtros opcionales).\n"
        "- search_files: Buscar archivos por nombre o contenido.\n"
        "- read_file: Leer el contenido de un archivo (Docs, Sheets, texto).\n"
        "- create_document: Crear un nuevo Google Doc con contenido inicial.\n"
        "- upload_file: Subir un archivo local a Drive.\n"
        "- delete_file: Mover un archivo a la papelera.\n"
        "- share_file: Compartir un archivo con otro usuario.\n\n"
        "Responde siempre en el idioma del usuario. Sé conciso y directo."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_DRIVE_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def drive_node(state: MessagesState) -> dict:
    """Nodo que procesa tareas de Google Drive usando un agente ReAct interno."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
