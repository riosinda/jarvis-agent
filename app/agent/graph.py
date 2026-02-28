from app.agent.select_llm import get_llm
from langgraph.prebuilt import create_react_agent

from app.agent.memory import checkpointer
from app.agent.prompts import build_prompt
from app.agent.tools import agent_tools
from app.core.config import settings

llm = get_llm()

agent = create_react_agent(
    model=llm,
    tools=agent_tools,
    prompt=build_prompt,
    checkpointer=checkpointer,
)