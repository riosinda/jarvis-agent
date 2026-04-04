"""Nodo Writer — genera reportes en Markdown, DOCX, PDF y formatea referencias APA."""

from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent

from app.agents.select_llm import get_llm
from app.services.research.writer_tools import (
    format_apa_reference,
    write_docx_report,
    write_markdown_report,
    write_pdf_report,
)

# ── ReAct Agent ───────────────────────────────────────────────────────────────

_WRITER_TOOLS = [
    write_markdown_report,
    write_docx_report,
    write_pdf_report,
    format_apa_reference,
]

_SYSTEM = SystemMessage(
    content=(
        "Eres un agente especializado en redacción y generación de reportes de investigación. "
        "Usa las herramientas disponibles para escribir y exportar documentos.\n\n"
        "- write_markdown_report: Genera un reporte en formato .md.\n"
        "- write_docx_report: Genera un reporte en Word (.docx) con formato profesional "
        "y sección de referencias.\n"
        "- write_pdf_report: Genera un reporte en PDF con formato profesional.\n"
        "- format_apa_reference: Formatea una referencia bibliográfica en estilo APA 7.\n\n"
        "El contenido debe estar en formato Markdown usando ## para secciones. "
        "Cuando el usuario pida un reporte completo, estructura el contenido con "
        "secciones claras: Introducción, Desarrollo, Conclusiones y Referencias.\n\n"
        "Responde siempre en el idioma del usuario. Confirma la ruta del archivo generado."
    )
)


def _build_prompt(state: dict) -> list:
    return [_SYSTEM] + state.get("messages", [])


_agent = create_react_agent(model=get_llm(), tools=_WRITER_TOOLS, prompt=_build_prompt)


# ── Node function ─────────────────────────────────────────────────────────────


def writer_node(state: MessagesState) -> dict:
    """Nodo que genera reportes en Markdown, DOCX, PDF y formatea referencias APA."""
    result = _agent.invoke({"messages": state["messages"]})
    return {"messages": [result["messages"][-1]]}
