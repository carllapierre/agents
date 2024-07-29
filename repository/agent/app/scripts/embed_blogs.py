import json
import os
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import tiktoken

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def split_text_into_chunks(text, title, author, chunk_size=512):
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    
    text_with_metadata = f"Title: {title}\nAuthor: {author}\n"
    metadata_tokens = encoder.encode(text_with_metadata)
    
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk = tokens[i:i + chunk_size]
        chunk_text = encoder.decode(metadata_tokens + chunk)
        chunks.append(chunk_text)
    
    return chunks

def embed_text_chunks(text_chunks):
    embeddings = []
    for chunk in text_chunks:
        response = client.embeddings.create(input=chunk, model="text-embedding-ada-002")
        embeddings.append(response.data[0].embedding)
    return embeddings

def store_in_pinecone(text_chunks, embeddings, index_name):
    pinecone_client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pinecone_client.Index(name=index_name)
    
    for embedding, chunk in zip(embeddings, text_chunks):
        meta = {
            'text': chunk,
        }
        # generate random uuid
        index.upsert(vectors=[(str(uuid.uuid4()), embedding, meta)])

def process_file(file_path, index_name):
    data = load_json(file_path)
    title = data.get('title', 'Unknown')
    author = data.get('author', 'Unknown')
    text = data.get('text', '')

    text_chunks = split_text_into_chunks(text, title, author)
    embeddings = embed_text_chunks(text_chunks)
    store_in_pinecone(text_chunks, embeddings,index_name)

def main(data_directory, index_name):
    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            file_path = os.path.join(data_directory, filename)
            process_file(file_path, index_name)

if __name__ == '__main__':
    data_directory = '../data'
    index_name = 'osedea-blogs'
    main(data_directory, index_name)
