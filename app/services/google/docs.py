from app.core.google_auth import get_docs_service, get_drive_service
from typing import Optional


def google_docs_get(document_id: str) -> str:
    """Obtiene el contenido completo de un Google Doc.

    Args:
        document_id: ID del documento de Google Docs.

    Returns:
        Título y contenido del documento en texto plano, o descripción del error.
    """
    try:
        service = get_docs_service()
        doc = service.documents().get(documentId=document_id).execute()

        title = doc.get("title", "Sin título")
        content = ""

        for block in doc.get("body", {}).get("content", []):
            paragraph = block.get("paragraph")
            if paragraph:
                for element in paragraph.get("elements", []):
                    text_run = element.get("textRun")
                    if text_run:
                        content += text_run.get("content", "")

        return f"Título: {title}\n\nContenido:\n{content}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al obtener el documento: {e}"


def google_docs_create(title: str, content: str = "", folder_id: Optional[str] = None) -> str:
    """Crea un nuevo Google Doc con contenido inicial.

    Args:
        title: Título del documento.
        content: Contenido inicial del documento (opcional).
        folder_id: ID de la carpeta en Drive donde guardar el doc (opcional).

    Returns:
        Mensaje de confirmación con el ID y link del documento, o descripción del error.
    """
    try:
        drive_service = get_drive_service()
        docs_service = get_docs_service()

        # Crear el documento vacío via Drive
        file_metadata = {
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]

        doc = drive_service.files().create(
            body=file_metadata, fields="id, webViewLink"
        ).execute()
        doc_id = doc["id"]

        # Insertar contenido si se proporcionó
        if content:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {"insertText": {"location": {"index": 1}, "text": content}}
                    ]
                },
            ).execute()

        return (
            f"Documento creado correctamente.\n"
            f"ID: {doc_id}\n"
            f"Link: {doc.get('webViewLink')}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al crear el documento: {e}"


def google_docs_append(document_id: str, content: str) -> str:
    """Agrega texto al final de un Google Doc existente.

    Args:
        document_id: ID del documento.
        content: Texto a agregar al final del documento.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_docs_service()

        # Obtener el índice del último carácter
        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1

        service.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": end_index},
                            "text": content,
                        }
                    }
                ]
            },
        ).execute()

        return f"Contenido agregado al documento {document_id} correctamente."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al agregar contenido: {e}"


def google_docs_replace_text(document_id: str, old_text: str, new_text: str) -> str:
    """Reemplaza un texto específico dentro de un Google Doc.

    Args:
        document_id: ID del documento.
        old_text: Texto a buscar y reemplazar.
        new_text: Texto nuevo que reemplazará al anterior.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_docs_service()

        service.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {"text": old_text, "matchCase": True},
                            "replaceText": new_text,
                        }
                    }
                ]
            },
        ).execute()

        return f"Texto reemplazado correctamente en el documento {document_id}."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al reemplazar texto: {e}"


def google_docs_insert_at(document_id: str, content: str, index: int = 1) -> str:
    """Inserta texto en una posición específica de un Google Doc.

    Args:
        document_id: ID del documento.
        content: Texto a insertar.
        index: Índice de posición donde insertar (1 = inicio del documento).

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_docs_service()

        service.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {"insertText": {"location": {"index": index}, "text": content}}
                ]
            },
        ).execute()

        return f"Texto insertado en el índice {index} del documento {document_id}."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al insertar texto: {e}"


def google_docs_clear(document_id: str) -> str:
    """Borra todo el contenido de un Google Doc.

    Args:
        document_id: ID del documento a limpiar.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_docs_service()

        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1

        if end_index <= 1:
            return "El documento ya está vacío."

        service.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "deleteContentRange": {
                            "range": {"startIndex": 1, "endIndex": end_index}
                        }
                    }
                ]
            },
        ).execute()

        return f"Documento {document_id} limpiado correctamente."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al limpiar el documento: {e}"


def google_docs_overwrite(document_id: str, new_content: str) -> str:
    """Reemplaza todo el contenido de un Google Doc con texto nuevo.

    Args:
        document_id: ID del documento.
        new_content: Nuevo contenido que reemplazará todo el texto actual.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_docs_service()

        # Primero limpiar
        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1

        requests = []
        if end_index > 1:
            requests.append(
                {
                    "deleteContentRange": {
                        "range": {"startIndex": 1, "endIndex": end_index}
                    }
                }
            )

        # Luego insertar nuevo contenido
        requests.append(
            {"insertText": {"location": {"index": 1}, "text": new_content}}
        )

        service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        return f"Documento {document_id} actualizado correctamente."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al sobreescribir el documento: {e}"