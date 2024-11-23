# pip install streamlit langchain lanchain-openai beautifulsoup4 python-dotenv chromadb

import streamlit as st
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from bs4 import BeautifulSoup
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles




from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500/get_response/"],  # Allow all origins, or specify the file URL: ["file:///F:/index.html"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods like GET, POST, etc.
    allow_headers=["*"],  # Allow all headers
)




# A placeholder to simulate vector store and chat history storage
session_data = {
    "vector_store": None,
    "chat_history": []
}

# Define User Input model
class UserInput(BaseModel):
    question: str

# Define Persist Directory and Embedding Model
persist_directory = "./chroma_db"
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Example: a commonly used open-source model

# Define prompt template
prompt_template = """
You are an intelligent assistant that has access to the content of a specific provided website. Your task is to answer the user's questions solely based on the content from this website.

Please make sure your response is based only on the information provided on the website. 

Do not use any outside knowledge at all. If it is not available on the website, simply say 'I could not find the answer for this question'.

Chat History:
{chat_history}

User's Question:
{question}

Answer based strictly on the website content:
"""
prompt = PromptTemplate(input_variables=["chat_history", "question"], template=prompt_template)


def get_all_links(base_url: str) -> set:
    """
    Fetch all internal links from the given base URL.
    """
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    base_domain = requests.utils.urlparse(base_url).netloc

    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if not href.startswith('http'):  # Handle relative links
            href = requests.compat.urljoin(base_url, href)
        # Only include links within the same domain
        if base_domain in requests.utils.urlparse(href).netloc:
            links.add(href)
    return links


def get_vectorstore_from_url(url: str):
    """
    Create a vector store from all pages linked from the provided URL.
    """
    # Get all linked pages from the base URL
    links = get_all_links(url)
    
    all_documents = []
    for link in links:
        try:
            # Load the content of each page
            loader = WebBaseLoader(link)
            document = loader.load()
            all_documents.extend(document)
        except Exception as e:
            print(f"Error loading {link}: {e}")

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(all_documents)
    
    # Create a vectorstore from the chunks using open-source embeddings
    vector_store = Chroma.from_documents(document_chunks, embedding_model, persist_directory=persist_directory)
    
    return vector_store


def get_context_retriever_chain(vector_store):
    # Convert vector store to retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # Set up the language model
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        max_retries=2,
        api_key="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"  # Ensure API key is loaded from the environment
    )

    # Create the LLMChain with the prompt and LLM
    prompt_chain = LLMChain(llm=llm, prompt=prompt)

    # Create the ConversationalRetrievalChain with the prompt chain
    retriever_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,  # Set to True if you need the source documents as well
        verbose=True  # Optional, to debug the chain
    )
    
    return retriever_chain


@app.post("/get_response/")
async def get_response(user_input: UserInput):
    """
    Endpoint to generate a response based on the content of the provided website.
    """
    # Ensure that the vector store is already set up
    if session_data["vector_store"] is None:
        # Example URL, you should replace this with the actual URL you want to scrape
        session_data["vector_store"] = get_vectorstore_from_url("https://www.travellofoodie.com/")
    
    # Get the retriever chain using the vector store
    retriever_chain = get_context_retriever_chain(session_data["vector_store"])
    
    # Prepare the input data with the correct key
    input_data = {
        "chat_history": session_data["chat_history"],
        "question": user_input.question  # Using the 'question' from the input
    }
    
    # Generate the response using the retriever chain
    try:
        response = retriever_chain.invoke(input_data)
        return {"answer": response['answer']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.post("/get_all_links/")
async def get_all_links_from_url(request: UserInput):
    """
    Endpoint to fetch all internal links from the given base URL.
    """
    try:
        links = get_all_links(request.question)  # Using the question field as the base URL
        return {"links": list(links)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching links: {str(e)}")
# Serve static files (CSS, JS, images)
# Mount the 'static' folder to serve CSS, JS, and other assets
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_chatbot_page():
    # Serve the chatbot HTML page
    return HTMLResponse(content=open("static/templates/chatbot.html").read())