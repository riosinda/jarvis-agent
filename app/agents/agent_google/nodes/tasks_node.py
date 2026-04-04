"""Nodo Tasks — agente especializado en Google Tasks."""

from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.google.tasks import (
    google_complete_task,
    google_create_task,
    google_delete_task,
    google_list_task_lists,
    google_list_tasks,
    google_update_task,
)

# ── Tools ─────────────────────────────────────────────────────────────────────


@tool
def list_task_lists() -> str:
    """Lista todas las listas de tareas disponibles en Google Tasks."""
    return google_list_task_lists()


@tool
def list_tasks(tasklist_id: str = "@default", show_completed: bool = False) -> str:
    """Lista las tareas de una lista específica.

    Args:
        tasklist_id: ID de la lista (usa '@default' para la lista principal).
        show_completed: Si es True, incluye tareas completadas.
    """
    return google_list_tasks(tasklist_id, show_completed)


@tool
def create_task(
    title: str,
    notes: str = "",
    due_date: Optional[str] = None,
    tasklist_id: str = "@default",
) -> str:
    """Crea una nueva tarea en Google Tasks.

    Args:
        title: Título de la tarea.
        notes: Notas o descripción (opcional).
        due_date: Fecha límite en formato 'YYYY-MM-DD' (opcional).
        tasklist_id: ID de la lista donde crear la tarea.
    """
    return google_create_task(title, notes, due_date, tasklist_id)


@tool
def complete_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Marca una tarea como completada.

    Args:
        task_id: ID de la tarea.
        tasklist_id: ID de la lista que contiene la tarea.
    """
    return google_complete_task(task_id, tasklist_id)


@tool
def update_task(
    task_id: str,
    tasklist_id: str = "@default",
    title: Optional[str] = None,
    notes: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Actualiza una tarea existente.

    Args:
        task_id: ID de la tarea a actualizar.
        tasklist_id: ID de la lista que contiene la tarea.
        title: Nuevo título (opcional).
        notes: Nuevas notas (opcional).
        due_date: Nueva fecha límite en formato 'YYYY-MM-DD' (opcional).
    """
    return google_update_task(task_id, tasklist_id, title, notes, due_date)


@tool
def delete_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Elimina una tarea de Google Tasks.

    Args:
        task_id: ID de la tarea a eliminar.
        tasklist_id: ID de la lista que contiene la tarea.
    """
    return google_delete_task(task_id, tasklist_id)


# ── ReAct Agent ───────────────────────────────────────────────────────────────

_TASKS_TOOLS = [list_task_lists, list_tasks, create_task, complete_task, update_task, delete_task]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en Google Tasks. Gestiona las tareas "
        "del usuario usando las herramientas disponibles.\n\n"
        "- list_task_lists: Listar todas las listas de tareas.\n"
        "- list_tasks: Listar tareas de una lista (pendientes o completadas).\n"
        "- create_task: Crear una nueva tarea con título, notas y fecha límite.\n"
        "- complete_task: Marcar una tarea como completada.\n"
        "- update_task: Actualizar título, notas o fecha límite de una tarea.\n"
        "- delete_task: Eliminar una tarea.\n\n"
        "Responde siempre en el idioma del usuario. Sé conciso y directo."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_TASKS_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def tasks_node(state: MessagesState) -> dict:
    """Nodo que procesa tareas de Google Tasks usando un agente ReAct interno."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
