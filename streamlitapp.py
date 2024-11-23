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




load_dotenv()

persist_directory = "./chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # Example: a commonly used open-source model from Hugging Face
)

# Define your custom prompt template
prompt_template = """
You are an intelligent assistant that has access to the content of a specific provided website. Your task is to answer the user's questions solely based on the content from this website.

Please make sure your response is based only on the information provided on the website. 

Do not use any outside knowledge at all.If it is not available on the website simply say i could not find the answer for this question

Chat History:
{chat_history}

User's Question:
{question}

Answer based strictly on the website content:
"""
# Create the prompt template
prompt = PromptTemplate(input_variables=["chat_history", "question"], template=prompt_template)



def get_all_links(base_url):
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

def get_vectorstore_from_url(url):
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
        api_key=" "
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

def get_response(user_input):
    # Ensure that the vector store is already set up in session state
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url("your_website_url_here")
    
    # Get the retriever chain using the vector store
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    
    # Prepare the input with the correct key
    input_data = {
        "chat_history": st.session_state.chat_history,
        "question": user_input  # Ensure the input key is 'question'
    }
    
    # Generate the response using the retriever chain
    response = retriever_chain.invoke(input_data)
    
    return response['answer']




# app config
st.set_page_config(page_title="Chat with websites", page_icon="🤖")
st.title("Chat with websites")

# sidebar
with st.sidebar:
    st.header("Settings")
    website_url = st.text_input("Website URL")

if website_url is None or website_url == "":
    st.info("Please enter a website URL")

else:
    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I am a bot. How can I help you?"),
        ]
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(website_url)    

    # user input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))
        
       

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)

    

  