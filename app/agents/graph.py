"""Grafo principal — Jarvis supervisor multi-agente."""

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from pydantic import BaseModel

from app.agents.memory import checkpointer
from app.agents.select_llm import get_llm
from app.agents.tools import general_tools
from app.agents.agent_google.graph import google_subgraph
from app.agents.agent_researcher.graph import researcher_subgraph

# ── General Node ──────────────────────────────────────────────────────────────

_GENERAL_SYSTEM = SystemMessage(
    content=(
        "Te llamas Jarvis, eres un asistente de inteligencia artificial diseñado "
        "para ayudar a los usuarios con una variedad de tareas generales.\n\n"
        "Herramientas disponibles:\n"
        "- get_current_datetime: Obtener la fecha y hora actuales de una zona horaria.\n"
        "- researcher: Buscar información actualizada en la web sobre cualquier tema.\n\n"
        "Directrices:\n"
        "- Cuando necesites saber la fecha u hora actual, usa SIEMPRE get_current_datetime.\n"
        "- Para preguntas que requieran información actualizada, usa researcher.\n"
        "- Responde siempre en el idioma del usuario.\n"
        "- Sé conciso pero amable."
    )
)


def _build_general_prompt(state: dict) -> list:
    return [_GENERAL_SYSTEM] + state.get("messages", [])


_general_react_agent = create_react_agent(
    model=get_llm(),
    tools=general_tools,
    prompt=_build_general_prompt,
)


def general_node(state: MessagesState) -> dict:
    """Nodo general: maneja preguntas, fecha/hora e investigación web."""
    result = _general_react_agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}


# ── Jarvis Supervisor ─────────────────────────────────────────────────────────

_JARVIS_ROUTING_SYSTEM = SystemMessage(
    content=(
        "Eres Jarvis, el supervisor principal. Analiza el mensaje del usuario y decide "
        "a qué nodo delegar la tarea.\n\n"
        "Nodos disponibles:\n"
        "- google_node: Todo lo relacionado con servicios de Google — Gmail (correos), "
        "Calendar (agenda, eventos), Tasks (tareas pendientes), Drive (archivos) "
        "y Docs (documentos).\n"
        "- researcher_node: Investigación y búsqueda de información — búsqueda web, "
        "artículos académicos (ArXiv, PubMed), y generación de reportes (PDF, Word).\n"
        "- general_node: Consultar la hora/fecha actual y conversación general sin "
        "necesidad de búsqueda ni herramientas Google.\n\n"
        "Responde ÚNICAMENTE con 'google_node', 'researcher_node' o 'general_node'."
    )
)

_JarvisNext = Literal["google_node", "researcher_node", "general_node"]


class _JarvisRoute(BaseModel):
    next: _JarvisNext


_llm = get_llm()


def jarvis_supervisor(state: MessagesState) -> Command[Literal["google_node", "researcher_node", "general_node"]]:
    """Supervisor Jarvis: enruta al nodo correcto según la intención del usuario."""
    messages = [_JARVIS_ROUTING_SYSTEM] + state["messages"]
    response = _llm.with_structured_output(_JarvisRoute).invoke(messages)
    return Command(goto=response.next)


# ── Build main graph ──────────────────────────────────────────────────────────

_builder = StateGraph(MessagesState)

_builder.add_node("jarvis_supervisor", jarvis_supervisor)
_builder.add_node("google_node", google_subgraph)
_builder.add_node("researcher_node", researcher_subgraph)
_builder.add_node("general_node", general_node)

_builder.add_edge(START, "jarvis_supervisor")
_builder.add_edge("google_node", END)
_builder.add_edge("researcher_node", END)
_builder.add_edge("general_node", END)

agent = _builder.compile(checkpointer=checkpointer)
