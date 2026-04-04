"""Subgrafo Researcher — supervisor que orquesta búsqueda web, académica y escritura."""

from typing import Literal

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from app.agents.select_llm import get_llm
from app.agents.agent_researcher.nodes.academic_search_node import academic_search_node
from app.agents.agent_researcher.nodes.web_search_node import web_search_node
from app.agents.agent_researcher.nodes.writer_node import writer_node

# ── Researcher Supervisor ──────────────────────────────────────────────────────

_RESEARCHER_MEMBERS = ["web_search_node", "academic_search_node", "writer_node"]

_ROUTING_SYSTEM = SystemMessage(
    content=(
        "Eres el supervisor del agente investigador. Analiza el contexto de la conversación "
        "y decide qué nodo especializado debe actuar a continuación.\n\n"
        "Nodos disponibles:\n"
        "- web_search_node: Búsquedas generales en la web usando DuckDuckGo, Tavily "
        "y Wikipedia. Úsalo para noticias, preguntas generales e información actualizada.\n"
        "- academic_search_node: Búsqueda de papers y artículos científicos en ArXiv, "
        "PubMed y Semantic Scholar. Úsalo cuando se pidan fuentes académicas o papers.\n"
        "- writer_node: Redacta y exporta reportes en Markdown, Word o PDF, y formatea "
        "referencias APA. Úsalo cuando el usuario pida generar un documento o reporte.\n"
        "- FINISH: La investigación está completa y no se necesitan más nodos.\n\n"
        "Responde ÚNICAMENTE con el nombre exacto del nodo o con 'FINISH'."
    )
)

_ResearcherNext = Literal["web_search_node", "academic_search_node", "writer_node", "FINISH"]


class _ResearcherRoute(BaseModel):
    next: _ResearcherNext


_llm = get_llm()


def researcher_supervisor(state: MessagesState) -> Command[Literal[*_RESEARCHER_MEMBERS, "__end__"]]:
    """Supervisor que enruta al nodo de investigación especializado correcto."""
    messages = [_ROUTING_SYSTEM] + state["messages"]
    response = _llm.with_structured_output(_ResearcherRoute).invoke(messages)

    if response.next == "FINISH":
        return Command(goto=END)

    return Command(goto=response.next)


# ── Build subgraph ─────────────────────────────────────────────────────────────

_builder = StateGraph(MessagesState)

_builder.add_node("researcher_supervisor", researcher_supervisor)
_builder.add_node("web_search_node", web_search_node)
_builder.add_node("academic_search_node", academic_search_node)
_builder.add_node("writer_node", writer_node)

_builder.add_edge(START, "researcher_supervisor")

# Cada nodo hoja regresa al supervisor para que evalúe si la tarea está completa
for _member in _RESEARCHER_MEMBERS:
    _builder.add_edge(_member, "researcher_supervisor")

researcher_subgraph = _builder.compile()
