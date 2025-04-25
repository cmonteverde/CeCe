import os
from langchain.llms import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import DataFrameLoader
import pandas as pd
from dotenv import load_dotenv
import vector_store
import streamlit as st

# Load environment variables
load_dotenv()

# Get API keys from environment variables
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
openai_api_key = os.getenv("OPENAI_API_KEY", "")

# Initialize LLM based on available API keys and configuration
def get_llm(provider="DeepSeek-V3"):
    if provider == "DeepSeek-V3":
        llm = HuggingFaceHub(
            repo_id="deepseek-ai/deepseek-llm-7b-chat",
            model_kwargs={"temperature": 0.7, "max_length": 512},
            huggingfacehub_api_token=huggingface_api_key
        )
    elif provider == "OpenAI":
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
    else:
        # Default to DeepSeek if provider not recognized
        llm = HuggingFaceHub(
            repo_id="deepseek-ai/deepseek-llm-7b-chat",
            model_kwargs={"temperature": 0.7, "max_length": 512},
            huggingfacehub_api_token=huggingface_api_key
        )
    
    return llm

# Initialize embeddings model
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

# Process dataset for RAG
def process_dataset_for_rag(df):
    # Create text representation of the dataset
    if df is None:
        return None
    
    # Create a summary of the dataset
    summary = [
        f"Dataset with {df.shape[0]} rows and {df.shape[1]} columns.",
        f"Columns: {', '.join(df.columns.tolist())}",
        f"Data types: {', '.join([f'{col}: {dtype}' for col, dtype in zip(df.columns, df.dtypes.astype(str))])}"
    ]
    
    # Add some sample data
    sample_data = []
    for i, row in df.head(5).iterrows():
        sample_data.append(f"Row {i}: {', '.join([f'{col}: {val}' for col, val in row.items()])}")
    
    # Add statistical summary
    stats = []
    for col in df.select_dtypes(include=['number']).columns:
        stats.append(f"Column {col} - min: {df[col].min()}, max: {df[col].max()}, mean: {df[col].mean()}, median: {df[col].median()}")
    
    # Combine all text
    text = "\n".join(summary + ["Sample data:"] + sample_data + ["Statistical summary:"] + stats)
    
    # Create a document for the vector store
    from langchain.docstore.document import Document
    doc = Document(page_content=text, metadata={"source": "uploaded_dataset"})
    
    return [doc]

# Create or retrieve vector store
def get_vector_store(df=None):
    # If df is provided, create a new vector store
    if df is not None:
        documents = process_dataset_for_rag(df)
        if documents:
            embeddings = get_embeddings()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            splits = text_splitter.split_documents(documents)
            vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)
            return vector_store
    
    # Otherwise, try to load from persistent storage
    try:
        embeddings = get_embeddings()
        vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        return vector_store
    except:
        # If no persistent store exists and no df provided, return None
        return None

# Process a query using RAG
def process_query(query, df=None):
    try:
        # Get the LLM
        llm = get_llm()
        
        # Get or create vector store
        vectorstore = get_vector_store(df)
        
        if vectorstore is None:
            # If no vector store is available, use the LLM directly
            climate_context = (
                "You are CeCe (Climate Copilot), an AI assistant specializing in climate and weather data analysis. "
                "You help users with climate data visualization, scientific calculations, and understanding weather patterns. "
                "If asked about specific data, mention you need a dataset to be uploaded first."
            )
            
            response = f"I'm CeCe, your Climate Copilot. {query} To give you a more specific answer, I would need you to upload a climate or weather dataset. Would you like me to help you with that?"
            return response
        
        # Create memory for conversation history
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Create the retrieval chain
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory,
            verbose=True
        )
        
        # Add system prompt to guide the model
        system_prompt = (
            "You are CeCe (Climate Copilot), an AI assistant specializing in climate and weather data analysis. "
            "You help users with climate data visualization, scientific calculations, and understanding weather patterns. "
            "Base your responses on the provided context and your knowledge of climate science."
        )
        
        # Run the query
        response = qa({"question": query, "system_prompt": system_prompt})
        
        return response["answer"]
    
    except Exception as e:
        # Fallback response in case of errors
        return f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your question."
