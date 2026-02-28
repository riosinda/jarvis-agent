from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # Selección de modelo
    LLM_PROVIDER: Literal["openai", "gemini", "ollama"] = "openai"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Ollama
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Parámetros compartidos
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096

    # Google OAuth
    GOOGLE_CREDENTIALS_PATH: str = "credentials.json"
    GOOGLE_TOKEN_PATH: str = "token.json"

    # Gmail API
    GMAIL_SENDER_EMAIL: str = ""
    GMAIL_SCOPES: list[str] = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/calendar",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()