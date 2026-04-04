from app.core.google_auth import get_gmail_service
from app.core.config import settings

from email.mime.text import MIMEText
import base64


def google_send_email(to: str, subject: str, body: str) -> str:
    """Envía un correo electrónico a través de Gmail.

    Args:
        to: Dirección de correo del destinatario.
        subject: Asunto del correo.
        body: Cuerpo del correo en texto plano.

    Returns:
        Mensaje de confirmación con el ID del correo enviado, o una descripción del error.
    """
    try:
        service = get_gmail_service()
        sender = settings.GMAIL_SENDER_EMAIL

        message = MIMEText(body)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )
        return f"Email enviado correctamente. Message ID: {sent['id']}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al enviar el email: {e}"


def google_list_emails(max_results: int = 10, query: str = "") -> str:
    """Lista los correos de la bandeja de entrada.

    Args:
        max_results: Número máximo de correos a retornar.
        query: Filtro de búsqueda (ej: 'is:unread', 'from:juan@gmail.com').

    Returns:
        Lista de correos con ID, remitente, asunto y fecha, o descripción del error.
    """
    try:
        service = get_gmail_service()
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results, q=query)
            .execute()
        )
        messages = results.get("messages", [])
        if not messages:
            return "No se encontraron correos."

        emails = []
        for msg in messages:
            detail = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )

            headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
            emails.append(
                f"ID: {msg['id']}\n"
                f"De: {headers.get('From')}\n"
                f"Asunto: {headers.get('Subject')}\n"
                f"Fecha: {headers.get('Date')}\n"
            )

        return "\n---\n".join(emails)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al listar correos: {e}"


def google_read_email(message_id: str) -> str:
    """Lee el contenido completo de un correo.

    Args:
        message_id: ID del correo a leer.

    Returns:
        Contenido completo del correo con remitente, asunto, fecha y cuerpo, o descripción del error.
    """
    try:
        service = get_gmail_service()
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

        body = ""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
        else:
            data = msg["payload"]["body"].get("data", "")
            body = base64.urlsafe_b64decode(data).decode("utf-8")

        return (
            f"De: {headers.get('From')}\n"
            f"Asunto: {headers.get('Subject')}\n"
            f"Fecha: {headers.get('Date')}\n"
            f"Cuerpo:\n{body}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al leer el correo: {e}"


def google_reply_email(message_id: str, body: str) -> str:
    """Responde a un correo existente manteniendo el hilo.

    Args:
        message_id: ID del correo al que se responde.
        body: Cuerpo de la respuesta.

    Returns:
        Mensaje de confirmación con el ID del correo enviado, o descripción del error.
    """
    try:
        service = get_gmail_service()
        sender = settings.GMAIL_SENDER_EMAIL

        original = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["From", "Subject", "Message-ID", "References"],
            )
            .execute()
        )

        headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
        thread_id = original["threadId"]

        message = MIMEText(body)
        message["to"] = headers.get("From")
        message["from"] = sender
        message["subject"] = f"Re: {headers.get('Subject', '')}"
        message["In-Reply-To"] = headers.get("Message-ID", "")
        message["References"] = headers.get("Message-ID", "")

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw, "threadId": thread_id})
            .execute()
        )

        return f"Respuesta enviada. Message ID: {sent['id']}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al responder el correo: {e}"


def google_mark_as_read(message_id: str) -> str:
    """Marca un correo como leído.

    Args:
        message_id: ID del correo.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return f"Correo {message_id} marcado como leído."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al marcar como leído: {e}"


def google_archive_email(message_id: str) -> str:
    """Archiva un correo (quita de la bandeja de entrada).

    Args:
        message_id: ID del correo.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId="me", id=message_id, body={"removeLabelIds": ["INBOX"]}
        ).execute()
        return f"Correo {message_id} archivado."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al archivar el correo: {e}"

