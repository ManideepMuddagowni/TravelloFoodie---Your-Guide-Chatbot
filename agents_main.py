from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from bs4 import BeautifulSoup
import requests
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging
import os
from urllib.parse import urlparse
from pathlib import Path
from crewai import Crew, Agent, Process
from agents import travel_itinerary_researcher, travel_itinerary_writer
from tasks import travel_itinerary_research_task, travel_itinerary_write_task

# FastAPI setup
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500/get_response/"],  # Allow specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods like GET, POST, etc.
    allow_headers=["*"],  # Allow all headers
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ALLOWED_URL = "https://www.travellofoodie.com/"
persist_directory = "./chroma_db"
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Example embedding model

# Placeholder for session data (vector store and chat history)
session_data = {
    "vector_store": None,
    "chat_history": []
}

# User Input model
class UserInput(BaseModel):
    question: str

# Utility to check and load/create the vector store
def load_or_create_vectorstore(url: str):
    """
    Load the vector store if it exists, otherwise scrape and create a new one.
    """
    if os.path.exists(persist_directory):
        logger.info(f"Loading existing vector store from {persist_directory}.")
        vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
    else:
        logger.info(f"Creating new vector store from {url}.")
        vector_store = get_vectorstore_from_url(url)
    return vector_store

# Scraping function to extract all links from the website
def get_all_links(base_url: str) -> set:
    if base_url != ALLOWED_URL:
        raise HTTPException(status_code=400, detail=f"Only {ALLOWED_URL} is allowed.")
    try:
        logger.info(f"Fetching links from {base_url}...")
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        base_domain = urlparse(base_url).netloc
        links = set()
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if not href.startswith('http'):
                href = requests.compat.urljoin(base_url, href)
            if urlparse(href).netloc == base_domain:
                links.add(href)
        logger.info(f"Found {len(links)} links.")
        return links
    except Exception as e:
        logger.error(f"Error fetching links from {base_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching links: {str(e)}")

# Vector store creation from scraped website content
def get_vectorstore_from_url(url: str):
    if url != ALLOWED_URL:
        raise HTTPException(status_code=400, detail="Only the fixed URL can be used to create the vector store.")
    links = get_all_links(url)
    all_documents = []
    for link in links:
        try:
            logger.info(f"Loading documents from {link}...")
            loader = WebBaseLoader(link)
            documents = loader.load()
            all_documents.extend(documents)
            logger.info(f"Successfully loaded {len(documents)} documents from {link}.")
        except Exception as e:
            logger.error(f"Error loading {link}: {e}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100, add_start_index=True)
    document_chunks = text_splitter.split_documents(all_documents)
    logger.info(f"Splitting documents into {len(document_chunks)} chunks.")
    vector_store = Chroma.from_documents(document_chunks, embedding_model, persist_directory=persist_directory)
    logger.info("Vector store created successfully.")
    return vector_store

# Conversational RAG Chain setup
def get_context_retriever_chain(vector_store):
    try:
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        logger.info("Retriever chain created successfully.")
        return retriever
    except Exception as e:
        logger.error(f"Error creating retriever chain: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize the retriever chain.")

def get_conversational_rag_chain(retriever_chain): 
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0,
        max_retries=2,
        api_key=""
    )
    prompt = ChatPromptTemplate.from_messages([(
        
        "system", """
        You are an intelligent assistant. Greet customers politely and answer their questions strictly based on the content provided on the specific website only.
        If the information is not available on provided specific website, respond with:
        'I couldn't find the information to this question on the website'
        verify with user and ask if they want to retrieve information from external resources.
        If user says 'yes' or 'okay' find best places to visit based on the given context:\n\n{context}
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

crew = Crew(
    agents=[travel_itinerary_researcher, travel_itinerary_writer],
    tasks=[travel_itinerary_research_task, travel_itinerary_write_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)

@app.post("/get_response/")
async def get_response(user_input: UserInput):
    logger.info(f"Received user input: {user_input.question}")
    if "http://" in user_input.question or "https://" in user_input.question:
        logger.warning(f"Invalid question: URLs are not allowed. User asked: {user_input.question}")
        return {"answer": "Only questions about the website 'https://www.travellofoodie.com/' are allowed."}
    if session_data["vector_store"] is None:
        logger.info("No vector store found in session, loading or creating it.")
        session_data["vector_store"] = load_or_create_vectorstore(ALLOWED_URL)
    retriever = get_context_retriever_chain(session_data["vector_store"])
    conversation_rag_chain = get_conversational_rag_chain(retriever)
    try:
        response = conversation_rag_chain.invoke({
            "chat_history": session_data["chat_history"],
            "input": user_input.question
        })
        if response['answer'].strip() == "":
            logger.info("No relevant answer found on the website.")
            consent_message = (
                "The information is not available on the website. "
                "Would you like us to fetch this information from external resources?"
                "Enter yes or no to continue....!!!! Please respond with 'yes' or 'no'."
            )
            session_data["chat_history"].append({"role": "assistant", "content": consent_message})
            return {"answer": consent_message}
        session_data["chat_history"].append({"role": "assistant", "content": response['answer']})
        return {"answer": response['answer']}
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        return {"answer": "Sorry, something went wrong."}

@app.post("/handle_consent/")
async def handle_consent(user_input: UserInput):
    logger.info(f"Received consent response: {user_input.question}")
    user_response = user_input.question.strip().lower()
    if user_response in ["yes", "okay", "ok"]:
        logger.info("User consented to fetch external information.")
        try:
            result = crew.kickoff(inputs={'question': session_data["chat_history"][-2]["content"]})
            fallback_response = result.get('output', 'No output generated by the agents')
            session_data["chat_history"].append({"role": "assistant", "content": fallback_response})
            return {"answer": fallback_response}
        except Exception as e:
            logger.error(f"Error retrieving information from external resources: {e}")
            return {"answer": "Here is the fetched external information at the moment."}
    elif user_response in ["no", "not now"]:
        logger.info("User declined to fetch external information.")
        return {"answer": "Understood. If you need further assistance, feel free to ask."}
    else:
        logger.warning("Received an invalid consent response.")
        return {"answer": "Please respond with 'yes' or 'no' to proceed."}

@app.post("/get_all_links/")
async def get_all_links_from_base_url():
    try:
        logger.info(f"Fetching all links from the base URL {ALLOWED_URL}.")
        links = get_all_links(ALLOWED_URL)
        return {"links": list(links)}
    except Exception as e:
        logger.error(f"Error fetching links: {e}")
        return {"error": "Failed to fetch links."}



# Serve static files (CSS, JS, images)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_chatbot_page():
    return HTMLResponse(content=open("static/templates/chatbot.html").read())
