# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from langgraph.checkpoint import MemorySaver
from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage 
from .templates import prompts 
from .modules.tools.coreference_result import coreference_result
from .modules.tools.chunks import chunks

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_KEY")

app = FastAPI()

# CORS origins
origins = [
    "http://localhost",
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

coref_output = [coreference_result]
chunks_output = [chunks]

def run_coreference(state: MessagesState):
    messages = state['messages']
    model = ChatOpenAI(openai_api_key=OPENAI_KEY,  model_name="gpt-4o-mini")
    
    tool_llm = model.bind_tools(coref_output)
    response = tool_llm.invoke(messages)

    # get text from tool_call
    print (response.additional_kwargs["tool_calls"])

    return {"messages": [response]}

def create_chunks(state: MessagesState):
    messages = state['messages']
    last_message = messages[-1]

    # call LLM to get chunks

    # return chunks as a list

    return {"messages": [last_message]}

# Define a new graph
workflow = StateGraph(MessagesState)
workflow.add_node("coref", run_coreference)
# workflow.add_node("chunker", create_chunks)
# workflow.add_edge("coref", "chunker")
workflow.set_entry_point("coref")

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
