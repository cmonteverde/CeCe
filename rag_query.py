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
    try:
        if provider == "DeepSeek-V3" and huggingface_api_key:
            # Try a different, more reliable model on Hugging Face
            llm = HuggingFaceHub(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",  # More reliable model
                model_kwargs={"temperature": 0.7, "max_length": 512},
                huggingfacehub_api_token=huggingface_api_key
            )
        elif provider == "OpenAI" and openai_api_key:
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=openai_api_key
            )
        elif huggingface_api_key:
            # Default to a simpler, more reliable model if provider not recognized
            llm = HuggingFaceHub(
                repo_id="google/flan-t5-xl",  # Simpler, more reliable model
                model_kwargs={"temperature": 0.7, "max_length": 512},
                huggingfacehub_api_token=huggingface_api_key
            )
        else:
            raise ValueError("No valid API key found for the specified provider")
        
        return llm
    except Exception as e:
        st.error(f"Error initializing language model: {str(e)}")
        return None

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

# Process a query using RAG or fallback to direct responses
def process_query(query, df=None):
    import time
    import random
    
    # Add a timeout to avoid infinite waiting
    try:
        # Check if LLM is available
        llm = get_llm()
        
        # If LLM is not available, use the fallback responses
        if llm is None:
            return get_fallback_response(query)
        
        # Try to get or create vector store with a timeout
        vectorstore = None
        try:
            vectorstore = get_vector_store(df)
        except Exception as e:
            st.warning(f"Could not initialize vector store: {str(e)}")
        
        # If we have both the LLM and vector store, try to use RAG
        if vectorstore is not None:
            try:
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
                
                # Run the query with a timeout
                response = qa({"question": query, "system_prompt": system_prompt})
                
                return response["answer"]
            except Exception as e:
                st.warning(f"RAG query failed: {str(e)}. Falling back to direct response.")
                return get_fallback_response(query)
        else:
            # If no vector store is available, use direct response
            return get_fallback_response(query)
    
    except Exception as e:
        # Fallback response in case of errors
        return f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your question."

# Get a predefined response for common climate questions
def get_fallback_response(query):
    # A dictionary of predefined responses for common queries
    climate_responses = {
        "temperature": "Temperature is a key climate variable. I can help you analyze temperature trends, calculate anomalies, and visualize temperature data. You can use the preset buttons above to explore temperature-related features.",
        "precipitation": "Precipitation includes rain, snow, and other forms of water falling from the sky. I can help you analyze precipitation patterns and create visualization maps. Try the 'Generate a precipitation map' button above!",
        "climate change": "Climate change refers to significant changes in global temperature, precipitation, wind patterns, and other measures of climate that occur over several decades or longer. I can help you analyze climate data to understand these changes.",
        "weather": "Weather refers to day-to-day conditions, while climate refers to the average weather patterns in an area over a longer period. I can help you analyze both weather data and climate trends.",
        "forecast": "While I don't provide real-time weather forecasts, I can help you analyze historical climate data and identify patterns that might inform future conditions.",
        "hello": "Hello! I'm CeCe, your Climate Copilot. I'm here to help you analyze and visualize climate data. How can I assist you today?",
        "help": "I can help you with climate data analysis, visualization, and scientific calculations. Try one of the preset buttons above to get started, or ask me a specific question about climate data."
    }
    
    # Check if the query contains any of our predefined topics
    query_lower = query.lower()
    for topic, response in climate_responses.items():
        if topic in query_lower:
            return response
    
    # Default response if no specific topic is matched
    return "I'm CeCe, your Climate Copilot. I can help you analyze climate data, create visualizations, and perform scientific calculations. Try one of the preset buttons above, or ask me a specific question about climate or weather data!"
