from langchain_community.tools import ArxivQueryRun, PubmedQueryRun
from langchain_community.utilities import ArxivAPIWrapper, PubMedAPIWrapper
from langchain_core.tools import tool
import urllib.request
import urllib.parse
import xmltodict
import json


# ── ArXiv ────────────────────────────────────────────────────────────────────────

@tool
def arxiv_search(query: str, max_results: int = 5) -> str:
    """Busca artículos científicos en ArXiv. Ideal para papers de IA, matemáticas,
    física, computación y ciencias naturales.

    Args:
        query: Término o tema a buscar.
        max_results: Número máximo de artículos a retornar.

    Returns:
        Lista de artículos con título, autores, resumen y link.
    """
    try:
        arxiv = ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(top_k_results=max_results, load_max_docs=max_results)
        )
        return arxiv.invoke(query)
    except Exception as e:
        return f"Error al buscar en ArXiv: {e}"


@tool
def arxiv_get_paper(arxiv_id: str) -> str:
    """Obtiene el detalle completo de un paper de ArXiv por su ID.

    Args:
        arxiv_id: ID del paper en ArXiv (ej: '2301.07041' o 'https://arxiv.org/abs/2301.07041').

    Returns:
        Título, autores, abstract, fecha y link del paper.
    """
    try:
        # Limpiar el ID si viene como URL
        arxiv_id = arxiv_id.replace("https://arxiv.org/abs/", "").strip()

        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        with urllib.request.urlopen(url) as response:
            data = xmltodict.parse(response.read())

        entry = data["feed"]["entry"]
        authors = entry.get("author", [])
        if isinstance(authors, dict):
            authors = [authors]
        author_names = ", ".join([a.get("name", "") for a in authors])

        return (
            f"Título: {entry.get('title', '').strip()}\n"
            f"Autores: {author_names}\n"
            f"Fecha: {entry.get('published', 'N/A')}\n"
            f"Abstract: {entry.get('summary', '').strip()}\n"
            f"Link: {entry.get('id', 'N/A')}\n"
        )
    except Exception as e:
        return f"Error al obtener paper de ArXiv: {e}"


# ── PubMed ───────────────────────────────────────────────────────────────────────

@tool
def pubmed_search(query: str, max_results: int = 5) -> str:
    """Busca artículos médicos y científicos en PubMed. Ideal para investigación
    en medicina, biología, farmacología y ciencias de la salud.

    Args:
        query: Término o tema a buscar.
        max_results: Número máximo de artículos a retornar.

    Returns:
        Lista de artículos con título, autores, resumen y link.
    """
    try:
        pubmed = PubmedQueryRun(
            api_wrapper=PubMedAPIWrapper(top_k_results=max_results)
        )
        return pubmed.invoke(query)
    except Exception as e:
        return f"Error al buscar en PubMed: {e}"


# ── Semantic Scholar ─────────────────────────────────────────────────────────────

@tool
def semantic_scholar_search(query: str, max_results: int = 5) -> str:
    """Busca artículos científicos en Semantic Scholar. Retorna papers con
    métricas de citación y referencias, útil para evaluar impacto académico.

    Args:
        query: Término o tema a buscar.
        max_results: Número máximo de artículos a retornar.

    Returns:
        Lista de papers con título, autores, año, citas y abstract.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/search"
            f"?query={encoded_query}&limit={max_results}"
            f"&fields=title,authors,year,abstract,citationCount,externalIds,openAccessPdf"
        )

        req = urllib.request.Request(url, headers={"User-Agent": "JarvisAgent/1.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())

        papers = data.get("data", [])
        if not papers:
            return "No se encontraron papers en Semantic Scholar."

        output = []
        for p in papers:
            authors = ", ".join([a.get("name", "") for a in p.get("authors", [])])
            pdf_link = (p.get("openAccessPdf") or {}).get("url", "N/A")
            doi = (p.get("externalIds") or {}).get("DOI", "N/A")

            output.append(
                f"Título: {p.get('title')}\n"
                f"Autores: {authors}\n"
                f"Año: {p.get('year', 'N/A')}\n"
                f"Citas: {p.get('citationCount', 0)}\n"
                f"DOI: {doi}\n"
                f"PDF: {pdf_link}\n"
                f"Abstract: {p.get('abstract', 'N/A')}\n"
            )

        return "\n---\n".join(output)
    except Exception as e:
        return f"Error al buscar en Semantic Scholar: {e}"


@tool
def semantic_scholar_get_citations(paper_id: str, max_results: int = 10) -> str:
    """Obtiene las referencias citadas por un paper específico en Semantic Scholar.

    Args:
        paper_id: ID del paper en Semantic Scholar o DOI (ej: '10.1145/3442188.3445922').
        max_results: Número máximo de referencias a retornar.

    Returns:
        Lista de papers citados con título, autores y año.
    """
    try:
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
            f"?limit={max_results}&fields=title,authors,year,externalIds"
        )

        req = urllib.request.Request(url, headers={"User-Agent": "JarvisAgent/1.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())

        references = data.get("data", [])
        if not references:
            return "No se encontraron referencias para este paper."

        output = []
        for ref in references:
            p = ref.get("citedPaper", {})
            authors = ", ".join([a.get("name", "") for a in p.get("authors", [])])
            doi = (p.get("externalIds") or {}).get("DOI", "N/A")
            output.append(
                f"Título: {p.get('title', 'N/A')}\n"
                f"Autores: {authors}\n"
                f"Año: {p.get('year', 'N/A')}\n"
                f"DOI: {doi}\n"
            )

        return "\n---\n".join(output)
    except Exception as e:
        return f"Error al obtener citas de Semantic Scholar: {e}"