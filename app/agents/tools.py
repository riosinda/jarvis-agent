"""Herramientas generales (no-Google) para el nodo general de Jarvis."""

import requests
from langchain_core.tools import tool

from app.services.researcher import researcher


# ── Date & Time Tool ─────────────────────────────────────────────────────────


@tool
def get_current_datetime(timezone: str = "America/Mexico_City") -> str:
    """Obtiene la fecha y hora actuales para una zona horaria dada.

    Args:
        timezone: Identificador de zona horaria válido (ej. 'America/Mexico_City',
                  'US/Eastern', 'Europe/London').

    Returns:
        Texto legible con la fecha, hora, día de la semana y zona horaria actuales.
    """
    try:
        response = requests.get(
            f"https://timeapi.io/api/time/current/zone?timeZone={timezone}",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        return (
            f"Fecha: {data['date']}\n"
            f"Hora: {data['time']}\n"
            f"Día: {data['dayOfWeek']}\n"
            f"Zona horaria: {data['timeZone']}"
        )
    except requests.exceptions.HTTPError:
        return (
            f"Timezone '{timezone}' no válida. "
            "Usa un identificador como 'America/Mexico_City', 'US/Eastern', 'Europe/Madrid', etc."
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al obtener la fecha/hora: {e}"


# ── Export ────────────────────────────────────────────────────────────────────

general_tools = [get_current_datetime, researcher]
