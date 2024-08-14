from langchain_core.tools import tool
import requests
from dotenv import load_dotenv
import os
from openai import OpenAI
from pinecone import Pinecone
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

#import templates
from app.templates import prompts

load_dotenv()

INDEX_NAME = 'osedea-blogs'
OPENAI_KEY = os.getenv('OPENAI_KEY')

def embed_query(query_text):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))
    response = client.embeddings.create(input=query_text, model="text-embedding-ada-002")
    return response.data[0].embedding

def query_pinecone(embeded_query):
    pinecone_client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pinecone_client.Index(name=INDEX_NAME)
    query_results = index.query(vector=embeded_query, top_k=10, include_metadata = True)
    return query_results

@tool
def get_public_fino(question: str):
    """Answers general public facing questions about Osedea"""
    embedding = embed_query(question)
    pinecone_results = query_pinecone(embedding)
    relevant_docs = pinecone_results['matches']

    model = ChatOpenAI(openai_api_key=OPENAI_KEY,  model_name="gpt-4o-mini")
    new_message = SystemMessage(content=prompts['rag'].format(question=question, context=relevant_docs))
    response = model.invoke([new_message])

    return response.content