# 🤖 Jarvis Agent

Asistente de IA construido con **LangGraph** + **FastAPI** que puede enviar correos por Gmail, agendar eventos en Google Calendar y consultar la fecha/hora actual. Soporta múltiples proveedores de LLM: **OpenAI**, **Google Gemini** y **Ollama** (modelos locales).

## Arquitectura

```
jarvis-agent/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── agent/
│   │   ├── graph.py            # ReAct agent (LangGraph)
│   │   ├── memory.py           # Checkpointer para memoria conversacional
│   │   ├── prompts.py          # System prompt + few-shot examples
│   │   ├── select_llm.py       # Selector dinámico de LLM
│   │   └── tools.py            # Tools: Gmail, Calendar, DateTime
│   ├── api/
│   │   ├── routes.py           # POST /chat/
│   │   └── schemas.py          # Request/Response models
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   └── google_auth.py      # OAuth2 helper para Google APIs
│   └── services/
│       └── chat_service.py     # Lógica de invocación del agente
├── chat_cli.py                 # Cliente CLI para probar el chatbot
├── pyproject.toml
└── .env                        # Variables de entorno (no commitear)
```

## Tools disponibles

| Tool | Descripción |
|------|-------------|
| `send_email` | Envía un correo electrónico vía Gmail API |
| `create_calendar_event` | Crea un evento en Google Calendar |
| `get_current_datetime` | Obtiene fecha y hora actual por zona horaria |

## Proveedores de LLM soportados

| Proveedor | Modelos | Requiere API Key |
|-----------|---------|-------------------|
| **OpenAI** | `gpt-4o-mini` (default), cualquier modelo de OpenAI | Sí (`OPENAI_API_KEY`) |
| **Gemini** | `gemini-2.5-flash` (default), cualquier modelo de Gemini | Sí (`GOOGLE_API_KEY`) |
| **Ollama** | `llama3.1` (default), cualquier modelo local | No (corre local) |

El proveedor se selecciona con la variable de entorno `LLM_PROVIDER`.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- Proyecto en Google Cloud con **Gmail API** y **Google Calendar API** habilitadas
- Credenciales OAuth2 tipo **Desktop app**
- **Según el proveedor de LLM elegido:**
  - **OpenAI:** una API key de [OpenAI](https://platform.openai.com/)
  - **Gemini:** una API key de [Google AI Studio](https://aistudio.google.com/)
  - **Ollama:** [Ollama](https://ollama.com/) instalado y corriendo localmente

## Setup

### 1. Clonar e instalar dependencias

```bash
git clone https://github.com/tu-usuario/jarvis-agent.git
cd jarvis-agent
uv sync
```

### 2. Configurar Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto (o usa uno existente)
3. Habilita **Gmail API** y **Google Calendar API**
4. Ve a **APIs & Services → Credentials**
5. Crea un **OAuth 2.0 Client ID** tipo **Desktop app**
6. Descarga el archivo JSON y guárdalo como `credentials.json` en la raíz del proyecto
7. Ve a **OAuth consent screen** → **Test users** y agrega tu email

### 3. Variables de entorno

Crea un archivo `.env` en la raíz. La configuración varía según el proveedor de LLM que elijas:

#### Opción A: OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini          # opcional, default: gpt-4o-mini

GMAIL_SENDER_EMAIL=tu-email@gmail.com
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
```

#### Opción B: Gemini

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-2.5-flash     # opcional, default: gemini-2.5-flash

GMAIL_SENDER_EMAIL=tu-email@gmail.com
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
```

#### Opción C: Ollama (modelos locales)

> Requiere tener [Ollama](https://ollama.com/) instalado y corriendo (`ollama serve`).

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1              # opcional, default: llama3.1
OLLAMA_BASE_URL=http://localhost:11434  # opcional, default: http://localhost:11434

GMAIL_SENDER_EMAIL=tu-email@gmail.com
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
```

Para descargar un modelo en Ollama:

```bash
ollama pull llama3.1
```

#### Variables compartidas (opcionales)

```env
TEMPERATURE=0.7    # default: 0.7
MAX_TOKENS=4096    # default: 4096
```

### 4. Ejecutar

Levanta el servidor:

```bash
uv run uvicorn app.main:app --reload
```

En otra terminal, corre el cliente CLI:

```bash
uv run python chat_cli.py
```

La primera vez que uses una tool de Google, se abrirá el navegador para autorizar los permisos. El token se guarda en `token.json` y se reutiliza automáticamente.

## API

### `POST /chat/?session_id={id}`

**Request:**
```json
{
  "message": "Manda un correo a pedro@gmail.com diciendo que la junta es mañana"
}
```

**Response:**
```json
{
  "session_id": "abc-123",
  "response": "Perfecto, voy a enviar el correo..."
}
```

### `GET /health`

Retorna `{"status": "ok"}`.

## Stack

- **LangGraph** — Orquestación del agente ReAct
- **LangChain** — Tools, prompts, chat models
- **OpenAI / Gemini / Ollama** — LLM (configurable vía `LLM_PROVIDER`)
- **FastAPI** — API REST
- **Google APIs** — Gmail y Calendar
- **pydantic-settings** — Configuración tipada desde `.env`