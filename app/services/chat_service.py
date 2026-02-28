from langchain_core.messages import HumanMessage, BaseMessage
from app.agent.graph import agent

def parse_agent_response(message: BaseMessage) -> str:

    content = message.content
    
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        return "".join(text_parts).strip()
    
    return str(content).strip()

async def handle_message(session_id: str, message: str) -> dict:
    config = {"configurable": {"thread_id": session_id}}

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=message)]}, 
        config=config
    )

    last_message = result["messages"][-1]
    
    clean_text = parse_agent_response(last_message)

    return {
        "session_id": session_id, 
        "response": clean_text
    }