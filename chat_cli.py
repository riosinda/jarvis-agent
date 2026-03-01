import requests
import uuid
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

BASE_URL = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())

console = Console()

def chat(message: str) -> str:
    response = requests.post(
        f"{BASE_URL}/chat/",
        params={"session_id": SESSION_ID},
        json={"message": message},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


def main():
    console.clear()
    console.print(
        Panel(
            Text(f"🤖 Jarvis Agent - Chat CLI\nSession ID: {SESSION_ID}", justify="center", style="bold cyan"),
            title="Bienvenido",
            border_style="cyan",
        )
    )
    console.print("[dim]Escribe 'salir', 'exit' o 'quit' para terminar.[/dim]\n")

    while True:
        try:
            # Entrada del usuario
            user_input = Prompt.ask("[bold green]Tú[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]¡Hasta luego![/bold red]")
            break

        user_input = user_input.strip()

        if not user_input:
            continue

        if user_input.lower() in ("salir", "exit", "quit"):
            console.print("\n[bold cyan]🤖 Jarvis:[/bold cyan] [italic]¡Hasta luego! Que tengas un excelente día.[/italic]")
            break

        try:
            # Mostrar spinner mientras procesa (sin bloquear la petición de fondo, pero mostrando feedback visual)
            with console.status("[bold blue]Jarvis está pensando...[/bold blue]", spinner="dots"):
                reply = chat(user_input)

            # Mostrar la respuesta renderizando el Markdown (útil si hay viñetas, tablas, etc)
            console.print()
            console.print(Panel(Markdown(reply), title="[bold blue]🤖 Jarvis[/bold blue]", title_align="left", border_style="blue"))
            console.print()

        except requests.ConnectionError:
            console.print("\n[bold red]✖ Error:[/bold red] No se pudo conectar al servidor. ¿Está corriendo en localhost:8000?\n")
        except requests.HTTPError as e:
            console.print(f"\n[bold red]✖ Error {e.response.status_code}:[/bold red] {e.response.text}\n")
        except Exception as e:
            console.print(f"\n[bold red]✖ Error Inesperado:[/bold red] {e}\n")


if __name__ == "__main__":
    main()
