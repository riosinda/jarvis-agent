from langchain_core.messages import HumanMessage
from app.agent.graph import agent

async def handle_message(session_id: str, message: str) -> dict:

    config = {"configurable": {"thread_id": session_id}}

    result = await agent.ainvoke({"messages": [HumanMessage(content=message)]}, config=config)

    last_message = result["messages"][-1]
    response_text = last_message.content
    return {"session_id": session_id, "response": response_text}