"""Nodo Web Search — búsquedas generales en la web (DuckDuckGo, Tavily, Wikipedia)."""

from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.research.web_search_tools import (
    duckduckgo_search,
    duckduckgo_search_results,
    tavily_get_page_content,
    tavily_search,
    wikipedia_get_full_article,
    wikipedia_search,
)

# ── ReAct Agent ───────────────────────────────────────────────────────────────

_WEB_TOOLS = [
    duckduckgo_search,
    duckduckgo_search_results,
    tavily_search,
    tavily_get_page_content,
    wikipedia_search,
    wikipedia_get_full_article,
]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en búsqueda web. Busca y sintetiza información "
        "de la web usando las herramientas disponibles.\n\n"
        "- duckduckgo_search: Búsqueda general rápida en la web.\n"
        "- duckduckgo_search_results: Búsqueda con títulos, links y snippets detallados.\n"
        "- tavily_search: Búsqueda avanzada y estructurada, ideal para investigación.\n"
        "- tavily_get_page_content: Extrae el contenido completo de una URL específica.\n"
        "- wikipedia_search: Busca resúmenes de conceptos o temas en Wikipedia.\n"
        "- wikipedia_get_full_article: Obtiene el artículo completo de Wikipedia.\n\n"
        "Estrategia: para preguntas simples usa duckduckgo_search; para investigación "
        "profunda usa tavily_search; para definiciones y contexto usa wikipedia_search.\n\n"
        "Responde siempre en el idioma del usuario. Sintetiza los resultados de forma clara."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_WEB_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def web_search_node(state: MessagesState) -> dict:
    """Nodo que realiza búsquedas web usando DuckDuckGo, Tavily y Wikipedia."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
