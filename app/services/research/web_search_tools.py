from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
from tavily import TavilyClient
from app.core.config import settings


# ── DuckDuckGo General ───────────────────────────────────────────────────────────

@tool
def duckduckgo_search(query: str) -> str:
    """Realiza una búsqueda general en la web usando DuckDuckGo.

    Args:
        query: Término o pregunta a buscar.

    Returns:
        Resumen de los resultados encontrados en la web.
    """
    try:
        search = DuckDuckGoSearchRun()
        return search.invoke(query)
    except Exception as e:
        return f"Error al buscar en DuckDuckGo: {e}"


@tool
def duckduckgo_search_results(query: str, max_results: int = 5) -> str:
    """Busca en la web y retorna resultados detallados con título, link y snippet.

    Args:
        query: Término o pregunta a buscar.
        max_results: Número máximo de resultados a retornar.

    Returns:
        Lista de resultados con título, URL y descripción.
    """
    try:
        search = DuckDuckGoSearchResults(num_results=max_results)
        return search.invoke(query)
    except Exception as e:
        return f"Error al buscar resultados en DuckDuckGo: {e}"


# ── Tavily ───────────────────────────────────────────────────────────────────────

@tool
def tavily_search(query: str, max_results: int = 5) -> str:
    """Realiza una búsqueda avanzada en la web usando Tavily. Retorna resultados
    más precisos y estructurados que DuckDuckGo, ideal para investigación.

    Args:
        query: Término o pregunta a buscar.
        max_results: Número máximo de resultados.

    Returns:
        Resultados estructurados con título, URL, contenido y relevancia.
    """
    try:
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(query=query, max_results=max_results)

        output = []
        for r in response.get("results", []):
            output.append(
                f"Título: {r.get('title')}\n"
                f"URL: {r.get('url')}\n"
                f"Contenido: {r.get('content')}\n"
                f"Score: {r.get('score')}\n"
            )

        return "\n---\n".join(output) if output else "No se encontraron resultados."
    except Exception as e:
        return f"Error al buscar en Tavily: {e}"


@tool
def tavily_get_page_content(url: str) -> str:
    """Extrae el contenido completo de una página web usando Tavily.

    Args:
        url: URL de la página a extraer.

    Returns:
        Contenido completo de la página web.
    """
    try:
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.extract(urls=[url])

        results = response.get("results", [])
        if not results:
            return "No se pudo extraer contenido de la URL."

        return results[0].get("raw_content", "Sin contenido.")
    except Exception as e:
        return f"Error al extraer contenido de la página: {e}"


# ── Wikipedia ────────────────────────────────────────────────────────────────────

@tool
def wikipedia_search(query: str) -> str:
    """Busca información en Wikipedia. Ideal para contexto general, definiciones
    y conceptos establecidos.

    Args:
        query: Término o tema a buscar en Wikipedia.

    Returns:
        Resumen del artículo de Wikipedia encontrado.
    """
    try:
        wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2))
        return wiki.invoke(query)
    except Exception as e:
        return f"Error al buscar en Wikipedia: {e}"


@tool
def wikipedia_get_full_article(query: str) -> str:
    """Obtiene el artículo completo de Wikipedia sobre un tema.

    Args:
        query: Término o tema a buscar.

    Returns:
        Contenido completo del artículo de Wikipedia.
    """
    try:
        wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=10000)
        )
        return wiki.invoke(query)
    except Exception as e:
        return f"Error al obtener artículo de Wikipedia: {e}"