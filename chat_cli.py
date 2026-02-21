import requests
import uuid

BASE_URL = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())


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
    print("=" * 50)
    print("  Jarvis Agent - Chat CLI")
    print(f"  Session: {SESSION_ID}")
    print("  Escribe 'salir' o 'exit' para terminar")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nHasta luego!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("salir", "exit", "quit"):
            print("Hasta luego!")
            break

        try:
            reply = chat(user_input)
            print(f"\nJarvis: {reply}\n")
        except requests.ConnectionError:
            print("\n[Error] No se pudo conectar al servidor. ¿Está corriendo en localhost:8000?\n")
        except requests.HTTPError as e:
            print(f"\n[Error] {e.response.status_code}: {e.response.text}\n")
        except Exception as e:
            print(f"\n[Error] {e}\n")


if __name__ == "__main__":
    main()
