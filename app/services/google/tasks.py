from app.core.google_auth import get_tasks_service
from typing import Optional


def google_list_task_lists() -> str:
    """Lista todas las listas de tareas disponibles.

    Returns:
        Lista de task lists con ID y nombre, o descripción del error.
    """
    try:
        service = get_tasks_service()
        result = service.tasklists().list().execute()
        task_lists = result.get("items", [])

        if not task_lists:
            return "No hay listas de tareas."

        output = [f"ID: {tl['id']}\nNombre: {tl['title']}" for tl in task_lists]
        return "\n---\n".join(output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al listar task lists: {e}"


def google_list_tasks(tasklist_id: str = "@default", show_completed: bool = False) -> str:
    """Lista las tareas de una lista específica.

    Args:
        tasklist_id: ID de la lista de tareas (usa '@default' para la lista principal).
        show_completed: Si es True, incluye tareas completadas.

    Returns:
        Lista de tareas con ID, título, estado y fecha límite, o descripción del error.
    """
    try:
        service = get_tasks_service()
        result = (
            service.tasks()
            .list(
                tasklist=tasklist_id,
                showCompleted=show_completed,
                showHidden=show_completed,
            )
            .execute()
        )
        tasks = result.get("items", [])

        if not tasks:
            return "No hay tareas en esta lista."

        output = []
        for task in tasks:
            status = "✅" if task.get("status") == "completed" else "⬜"
            due = task.get("due", "Sin fecha límite")
            output.append(
                f"{status} ID: {task['id']}\n"
                f"   Título: {task.get('title', 'Sin título')}\n"
                f"   Fecha límite: {due}\n"
                f"   Notas: {task.get('notes', 'N/A')}\n"
            )

        return "\n".join(output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al listar tareas: {e}"


def google_create_task(
    title: str,
    notes: str = "",
    due_date: Optional[str] = None,
    tasklist_id: str = "@default",
) -> str:
    """Crea una nueva tarea en Google Tasks.

    Args:
        title: Título de la tarea.
        notes: Notas o descripción de la tarea (opcional).
        due_date: Fecha límite en formato 'YYYY-MM-DD' (opcional).
        tasklist_id: ID de la lista donde crear la tarea (usa '@default' para la principal).

    Returns:
        Mensaje de confirmación con el ID de la tarea, o descripción del error.
    """
    try:
        service = get_tasks_service()

        task = {"title": title, "notes": notes}

        if due_date:
            task["due"] = f"{due_date}T00:00:00.000Z"

        created = service.tasks().insert(tasklist=tasklist_id, body=task).execute()

        return (
            f"Tarea creada correctamente.\n"
            f"ID: {created['id']}\n"
            f"Título: {created['title']}\n"
            f"Fecha límite: {created.get('due', 'Sin fecha límite')}"
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al crear la tarea: {e}"


def google_complete_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Marca una tarea como completada.

    Args:
        task_id: ID de la tarea a completar.
        tasklist_id: ID de la lista que contiene la tarea.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_tasks_service()

        task = (
            service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        )
        task["status"] = "completed"

        updated = (
            service.tasks()
            .update(tasklist=tasklist_id, task=task_id, body=task)
            .execute()
        )

        return f"Tarea '{updated['title']}' marcada como completada. ✅"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al completar la tarea: {e}"


def google_update_task(
    task_id: str,
    tasklist_id: str = "@default",
    title: Optional[str] = None,
    notes: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Actualiza una tarea existente.

    Args:
        task_id: ID de la tarea a actualizar.
        tasklist_id: ID de la lista que contiene la tarea.
        title: Nuevo título de la tarea (opcional).
        notes: Nuevas notas de la tarea (opcional).
        due_date: Nueva fecha límite en formato 'YYYY-MM-DD' (opcional).

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_tasks_service()

        task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()

        if title:
            task["title"] = title
        if notes:
            task["notes"] = notes
        if due_date:
            task["due"] = f"{due_date}T00:00:00.000Z"

        updated = (
            service.tasks()
            .update(tasklist=tasklist_id, task=task_id, body=task)
            .execute()
        )

        return f"Tarea '{updated['title']}' actualizada correctamente."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al actualizar la tarea: {e}"


def google_delete_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Elimina una tarea de Google Tasks.

    Args:
        task_id: ID de la tarea a eliminar.
        tasklist_id: ID de la lista que contiene la tarea.

    Returns:
        Mensaje de confirmación o descripción del error.
    """
    try:
        service = get_tasks_service()
        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        return f"Tarea {task_id} eliminada correctamente."
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error al eliminar la tarea: {e}"