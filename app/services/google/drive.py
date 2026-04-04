from app.core.google_auth import get_drive_service
from typing import Optional
import io


def google_list_files(
    max_results: int = 10,
    query: str = "",
    folder_id: Optional[str] = None,
) -> str:
    """Lista archivos en Google Drive.

    Args:
        max_results: Número máximo de archivos a retornar.
        query: Filtro de búsqueda (ej: "name contains 'reporte'", "mimeType='application/pdf'").
        folder_id: ID de la carpeta donde buscar (opcional, busca en todo Drive si no se especifica).

    Returns:
        Lista de archivos con ID, nombre, tipo y fecha de modificación, o descripción del error.
    """
    try:
        service = get_drive_service()

        q_parts = []
        if query:
            q_parts.append(query)
        if folder_id:
            q_parts.append(f"'{folder_id}' in parents")
        q_parts.append("trashed = false")

        results = (
            service.files()
            .list(
                pageSize=max_results,
                q=" and ".join(q_parts),
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        files = results.get("files", [])
        if not files:
            return "No se encontraron archivos."

        output = []
        for f in files:
            size = f.get("size", "N/A")
            output.append(
                f"ID: {f['id']}\n"
                f"Nombre: {f['name']}\n"
                f"Tipo: {f['mimeType']}\n"
                f"Modificado: {f['modifiedTime']}\n"
                f"Tamaño: {size} bytes\n"
                f"Link: {f.get('webViewLink', 'N/A')}\n"
            )

        return "\n---\n".join(output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al listar archivos: {e}"


def google_search_files(search_term: str, max_results: int = 10) -> str:
    """Busca archivos en Google Drive por nombre o contenido.

    Args:
        search_term: Término de búsqueda.
        max_results: Número máximo de resultados.

    Returns:
        Lista de archivos encontrados o descripción del error.
    """
    try:
        service = get_drive_service()

        results = (
            service.files()
            .list(
                pageSize=max_results,
                q=f"fullText contains '{search_term}' and trashed = false",
                fields="files(id, name, mimeType, modifiedTime, webViewLink)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        files = results.get("files", [])
        if not files:
            return f"No se encontraron archivos con '{search_term}'."

        output = []
        for f in files:
            output.append(
                f"ID: {f['id']}\n"
                f"Nombre: {f['name']}\n"
                f"Tipo: {f['mimeType']}\n"
                f"Modificado: {f['modifiedTime']}\n"
                f"Link: {f.get('webViewLink', 'N/A')}\n"
            )

        return "\n---\n".join(output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al buscar archivos: {e}"


def google_read_file(file_id: str) -> str:
    """Lee el contenido de un archivo de Google Drive.
    Soporta Google Docs, Sheets, y archivos de texto plano.

    Args:
        file_id: ID del archivo a leer.

    Returns:
        Contenido del archivo como texto, o descripción del error.
    """
    try:
        service = get_drive_service()

        # Obtener metadata para saber el tipo
        file_meta = service.files().get(fileId=file_id, fields="mimeType, name").execute()
        mime_type = file_meta["mimeType"]
        name = file_meta["name"]

        # Exportar según tipo de archivo Google
        export_map = {
            "application/vnd.google-apps.document": "text/plain",
            "application/vnd.google-apps.spreadsheet": "text/csv",
            "application/vnd.google-apps.presentation": "text/plain",
        }

        if mime_type in export_map:
            content = (
                service.files()
                .export(fileId=file_id, mimeType=export_map[mime_type])
                .execute()
            )
            return f"Archivo: {name}\n\n{content.decode('utf-8')}"
        else:
            # Archivo binario o texto plano
            content = service.files().get_media(fileId=file_id).execute()
            try:
                return f"Archivo: {name}\n\n{content.decode('utf-8')}"
            except UnicodeDecodeError:
                return f"Archivo: {name}\nEl archivo es binario y no puede leerse como texto."

    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al leer el archivo: {e}"


def google_create_document(title: str, content: str = "", folder_id: Optional[str] = None) -> str:
    """Crea un nuevo Google Doc en Drive.

    Args:
        title: Título del documento.
        content: Contenido inicial del documento (opcional).
        folder_id: ID de la carpeta donde crear el documento (opcional).

    Returns:
        Mensaje de confirmación con el ID y link del documento, o descripción del error.
    """
    try:
        service = get_drive_service()

        file_metadata = {
            "name": title,
            "mimeType": "application/vnd.google-apps.document",
        }
        if folder_id:
            file_metadata["parents"] = [folder_id]

        doc = service.files().create(body=file_metadata, fields="id, webViewLink").execute()

        # Si hay contenido, escribirlo via Docs API
        if content:
            from app.core.google_auth import get_docs_service
            docs_service = get_docs_service()
            docs_service.documents().batchUpdate(
                documentId=doc["id"],
                body={
                    "requests": [
                        {"insertText": {"location": {"index": 1}, "text": content}}
                    ]
                },
            ).execute()

        return (
            f"Documento creado correctamente.\n"
            f"ID: {doc['id']}\n"
            f"Link: {doc.get('webViewLink')}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al crear el documento: {e}"


def google_upload_file(
    file_path: str,
    file_name: str,
    mime_type: str = "application/octet-stream",
    folder_id: Optional[str] = None,
) -> str:
    """Sube un archivo local a Google Drive.

    Args:
        file_path: Ruta local del archivo a subir.
        file_name: Nombre del archivo en Drive.
        mime_type: Tipo MIME del archivo (ej: 'application/pdf', 'image/png').
        folder_id: ID de la carpeta destino (opcional).

    Returns:
        Mensaje de confirmación con el ID y link del archivo, o descripción del error.
    """
    try:
        from googleapiclient.http import MediaFileUpload

        service = get_drive_service()

        file_metadata = {"name": file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

        uploaded = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )

        return (
            f"Archivo subido correctamente.\n"
            f"ID: {uploaded['id']}\n"
            f"Link: {uploaded.get('webViewLink')}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al subir el archivo: {e}"


def google_delete_file(file_id: str) -> str:
    """Elimina un archivo de Google Drive moviéndolo a la papelera.

    Args:
        file_id: ID del archivo a eliminar.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_drive_service()
        service.files().update(fileId=file_id, body={"trashed": True}).execute()
        return f"Archivo {file_id} movido a la papelera."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al eliminar el archivo: {e}"


def google_share_file(file_id: str, email: str, role: str = "reader") -> str:
    """Comparte un archivo de Google Drive con un usuario.

    Args:
        file_id: ID del archivo a compartir.
        email: Correo del usuario con quien compartir.
        role: Nivel de acceso ('reader', 'commenter', 'writer').

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_drive_service()

        permission = {"type": "user", "role": role, "emailAddress": email}

        service.permissions().create(
            fileId=file_id,
            body=permission,
            sendNotificationEmail=True,
        ).execute()

        return f"Archivo compartido con {email} como {role}."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al compartir el archivo: {e}"