from langchain_core.tools import tool
from app.core.google_auth import get_tasks_service # Asumiendo que agregarán esta función

# ── Google Tasks Tool ────────────────────────────────────────────────────────

@tool
def create_task(title: str, description: str = "") -> str:
    """Crea una nueva tarea en Google Tasks.

    Args:
        title: Título de la tarea.
        description: Descripción detallada o notas de la tarea (opcional).

    Returns:
        Mensaje de confirmación con el ID de la tarea creada, o una descripción del error.
    """
    try:
        # Mandamos a llamar el servicio ya autenticado
        service = get_tasks_service()
        
        task_body = {
            "title": title,
            "notes": description
        }  
        # Insertamos la tarea en la lista principal por defecto ('@default')
        result = (
            service.tasks()
            .insert(tasklist="@default", body=task_body)
            .execute()
        )

        return f"Tarea creada correctamente: {title} — ID: {result.get('id')}"
        
    except Exception as e:
        return f"Error al crear la tarea en Google Tasks: {e}"
    
@tool
def list_tasks(max_results: int = 10) -> str:
    """Obtiene la lista de tareas actuales en Google Tasks.
    
    Args:
        max_results: Número máximo de tareas a devolver (por defecto 10).
        
    Returns:
        Una cadena de texto con las tareas encontradas o un mensaje si la lista está vacía.
    """
    try:
        service = get_tasks_service()
        
        # Llamada a la API para obtener las tareas de la lista principal ('@default')
        results = service.tasks().list(
            tasklist='@default', 
            maxResults=max_results
        ).execute()
        
        tasks = results.get('items', [])
        
        if not tasks:
            return "Actualmente no tienes tareas en tu lista principal."
        
        # Formatear la lista de tareas para que Jarvis la pueda interpretar y leer fácilmente
        task_list_str = "Aquí están las tareas encontradas:\n"
        for task in tasks:
            # Revisar si la tarea está completada o pendiente
            status = "✅ Completada" if task.get('status') == 'completed' else "⏳ Pendiente"
            title = task.get('title', 'Sin título')
            
            task_list_str += f"{status} - {title}\n"
            
        return task_list_str
        
    except Exception as e:
        return f"Error al obtener las tareas en Google Tasks: {e}"