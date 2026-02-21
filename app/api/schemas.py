from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., example="Hello, how are you?")

class ChatResponse(BaseModel):
    session_id: str
    response: str = Field(..., example="I'm doing well, thank you!")