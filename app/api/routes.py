from fastapi import APIRouter, HTTPException
import traceback

from app.api.schemas import ChatRequest, ChatResponse
from app.services.chat_service import handle_message

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(session_id: str, body: ChatRequest):
    try:
        response = await handle_message(session_id, body.message)
        return response
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))