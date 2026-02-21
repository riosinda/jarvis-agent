from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.agent.memory import checkpointer
from app.agent.prompts import build_prompt
from app.agent.tools import agent_tools
from app.core.config import settings

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.OPENAI_TEMPERATURE,
    max_tokens=settings.OPENAI_MAX_TOKENS,
    api_key=settings.OPENAI_API_KEY,
)

agent = create_react_agent(
    model=llm,
    tools=agent_tools,
    prompt=build_prompt,
    checkpointer=checkpointer,
)