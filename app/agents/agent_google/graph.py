"""Subgrafo Google — supervisor que orquesta los nodos de servicios Google."""

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from app.agents.select_llm import get_llm
from app.agents.agent_google.nodes.calendar_node import calendar_node
from app.agents.agent_google.nodes.docs_node import docs_node
from app.agents.agent_google.nodes.drive_node import drive_node
from app.agents.agent_google.nodes.gmail_node import gmail_node
from app.agents.agent_google.nodes.tasks_node import tasks_node

# ── Google Supervisor ──────────────────────────────────────────────────────────

_GOOGLE_MEMBERS = ["gmail_node", "calendar_node", "tasks_node", "drive_node", "docs_node"]

_ROUTING_SYSTEM = SystemMessage(
    content=(
        "Eres el supervisor del ecosistema Google. Analiza el contexto de la conversación "
        "y decide qué agente especializado debe actuar a continuación.\n\n"
        "Agentes disponibles:\n"
        "- gmail_node: Correos (enviar, leer, listar, responder, archivar).\n"
        "- calendar_node: Calendario (crear, listar, actualizar, eliminar eventos, buscar huecos).\n"
        "- tasks_node: Tareas (crear, listar, completar, actualizar, eliminar).\n"
        "- drive_node: Drive (listar, buscar, leer, crear, subir, eliminar, compartir archivos).\n"
        "- docs_node: Docs (leer, crear, editar, agregar o reemplazar contenido).\n"
        "- FINISH: La tarea ya está completada, no se necesita ningún agente más.\n\n"
        "Responde ÚNICAMENTE con el nombre exacto del agente o con 'FINISH'."
    )
)

_GoogleNext = Literal["gmail_node", "calendar_node", "tasks_node", "drive_node", "docs_node", "FINISH"]


class _GoogleRoute(BaseModel):
    next: _GoogleNext


_llm = get_llm()


def google_supervisor(state: MessagesState) -> Command[Literal[*_GOOGLE_MEMBERS, "__end__"]]:
    """Supervisor que enruta al nodo Google especializado correcto."""
    messages = [_ROUTING_SYSTEM] + state["messages"]
    response = _llm.with_structured_output(_GoogleRoute).invoke(messages)

    if response.next == "FINISH":
        return Command(goto=END)

    return Command(goto=response.next)


# ── Build subgraph ─────────────────────────────────────────────────────────────

_builder = StateGraph(MessagesState)

_builder.add_node("google_supervisor", google_supervisor)
_builder.add_node("gmail_node", gmail_node)
_builder.add_node("calendar_node", calendar_node)
_builder.add_node("tasks_node", tasks_node)
_builder.add_node("drive_node", drive_node)
_builder.add_node("docs_node", docs_node)

_builder.add_edge(START, "google_supervisor")

# Cada nodo hoja regresa al supervisor para que evalúe si la tarea está completa
for _member in _GOOGLE_MEMBERS:
    _builder.add_edge(_member, "google_supervisor")

google_subgraph = _builder.compile()
