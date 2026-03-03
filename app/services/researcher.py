from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

# ── Busquedad tool ───────────────────────────────────────────────────────────────

@tool
def researcher(s: str) -> str:
    """Tool que busca información sobre algun tema en la web.
        Comienza la respuesta con 'estos son los resultados encontrados en la web'
        Usa la información que venga de la web
    """
    try:
        search = search = DuckDuckGoSearchRun()
        
        return search.invoke(s)
        
    except Exception as e:
        return f"Error al buscar {e}"