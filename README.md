# 🤖 Jarvis Agent

Asistente de IA construido con **LangGraph** + **FastAPI** que puede enviar correos por Gmail, agendar eventos en Google Calendar y consultar la fecha/hora actual.

## Arquitectura

```
jarvis-agent/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── agent/
│   │   ├── graph.py            # ReAct agent (LangGraph)
│   │   ├── memory.py           # Checkpointer para memoria conversacional
│   │   ├── prompts.py          # System prompt + few-shot examples
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

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- Proyecto en Google Cloud con **Gmail API** y **Google Calendar API** habilitadas
- Credenciales OAuth2 tipo **Desktop app**

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

Crea un archivo `.env` en la raíz:

```env
OPENAI_API_KEY=sk-...
GMAIL_SENDER_EMAIL=tu-email@gmail.com
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
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
- **OpenAI** — LLM (GPT-4o-mini por defecto)
- **FastAPI** — API REST
- **Google APIs** — Gmail y Calendar
- **pydantic-settings** — Configuración tipada desde `.env`