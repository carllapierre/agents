# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from typing import Annotated, Literal, TypedDict
from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.templates import prompts 
from app.tools.get_public_info import get_public_fino

# set_debug(True)

# Load environment variables
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")

app = FastAPI()

# CORS origins
origins = [
    "http://localhost",
    "http://localhost:8004",
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

content = {
    'core_prompt': None,
}

tools = [get_public_fino]
tool_node = ToolNode(tools)

# Define the function that determines whether to continue or not
def should_continue(state: MessagesState) -> Literal["tools", 'end']:
    messages = state['messages']
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    return "end"

# Define the function that calls the model
def call_model(state: MessagesState):
    messages = state['messages']
    model = ChatOpenAI(openai_api_key=OPENAI_KEY,  model_name="gpt-4o-mini")
    
    tool_llm = model.bind_tools(tools)
    response = tool_llm.invoke(messages)

    return {"messages": [response]}

def end(state: MessagesState):
    messages = state['messages']
    last_message = messages[-1]

    return {"messages": [last_message]}

# Define a new graph
workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_node("end", end)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

def get_response(prompt: str):
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)

    final_state = app.invoke(
        {"messages": [
            SystemMessage(content=prompts["system"]),
            HumanMessage(content=prompt)]},
        config={"configurable": {"thread_id": 42}}
    )

    return final_state["messages"][-1].content

# Pydantic model for the request body
class Prompt(BaseModel):
    prompt: str

@app.post("/inference")
async def inference(prompt_data: Prompt):
    response = get_response(prompt_data.prompt)
    return {"response": response}
