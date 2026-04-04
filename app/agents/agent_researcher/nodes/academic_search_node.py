"""Nodo Academic Search — búsqueda en fuentes académicas (ArXiv, PubMed, Semantic Scholar)."""

from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.research.academic_search_tools import (
    arxiv_get_paper,
    arxiv_search,
    pubmed_search,
    semantic_scholar_get_citations,
    semantic_scholar_search,
)

# ── ReAct Agent ───────────────────────────────────────────────────────────────

_ACADEMIC_TOOLS = [
    arxiv_search,
    arxiv_get_paper,
    pubmed_search,
    semantic_scholar_search,
    semantic_scholar_get_citations,
]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en investigación académica y científica. "
        "Busca papers, artículos y publicaciones usando las herramientas disponibles.\n\n"
        "- arxiv_search: Busca papers en ArXiv (IA, matemáticas, física, computación).\n"
        "- arxiv_get_paper: Obtiene detalles completos de un paper de ArXiv por ID.\n"
        "- pubmed_search: Busca artículos médicos y de ciencias de la salud en PubMed.\n"
        "- semantic_scholar_search: Busca papers con métricas de citación en Semantic Scholar.\n"
        "- semantic_scholar_get_citations: Obtiene las referencias de un paper específico.\n\n"
        "Estrategia: para IA/física/computación usa arxiv; para medicina usa pubmed; "
        "para evaluar impacto académico usa semantic_scholar.\n\n"
        "Responde siempre en el idioma del usuario. Incluye títulos, autores y links relevantes."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_ACADEMIC_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def academic_search_node(state: MessagesState) -> dict:
    """Nodo que busca en fuentes académicas: ArXiv, PubMed y Semantic Scholar."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
