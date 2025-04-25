import os
import pandas as pd
import numpy as np
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional
import tempfile
import io

# Initialize embedding model
def get_embedding_model():
    """
    Initialize and return the embedding model
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

# Initialize Chroma vector store
def init_vector_store(persist_directory: Optional[str] = None):
    """
    Initialize Chroma vector store
    
    Args:
        persist_directory: Directory to persist vector store (optional)
    
    Returns:
        Chroma vector store instance
    """
    embedding_model = get_embedding_model()
    
    if persist_directory:
        try:
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_model
            )
            return vector_store
        except:
            # If loading fails, create a new one
            vector_store = Chroma(
                embedding_function=embedding_model,
                persist_directory=persist_directory
            )
            return vector_store
    else:
        # In-memory vector store
        vector_store = Chroma(embedding_function=embedding_model)
        return vector_store

# Create documents from DataFrame
def create_documents_from_dataframe(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
    """
    Create documents from a DataFrame for vector store ingestion
    
    Args:
        df: Pandas DataFrame
        metadata: Additional metadata to add to documents
    
    Returns:
        List of Document objects
    """
    documents = []
    
    # Basic DataFrame info
    df_info = f"DataFrame with {df.shape[0]} rows and {df.shape[1]} columns.\n"
    df_info += f"Columns: {', '.join(df.columns.tolist())}\n"
    
    # Column statistics
    stats = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Statistics for numeric columns
            stats.append(f"Column '{col}' (numeric):")
            stats.append(f"  - Min: {df[col].min()}")
            stats.append(f"  - Max: {df[col].max()}")
            stats.append(f"  - Mean: {df[col].mean()}")
            stats.append(f"  - Median: {df[col].median()}")
            stats.append(f"  - Missing values: {df[col].isna().sum()}")
        elif pd.api.types.is_datetime64_dtype(df[col]):
            # Statistics for datetime columns
            stats.append(f"Column '{col}' (datetime):")
            stats.append(f"  - Min: {df[col].min()}")
            stats.append(f"  - Max: {df[col].max()}")
            stats.append(f"  - Missing values: {df[col].isna().sum()}")
        else:
            # Statistics for other columns
            stats.append(f"Column '{col}':")
            if df[col].nunique() < 10:
                stats.append(f"  - Unique values: {', '.join(map(str, df[col].unique()))}")
            else:
                stats.append(f"  - Unique values: {df[col].nunique()}")
            stats.append(f"  - Missing values: {df[col].isna().sum()}")
    
    df_stats = "\n".join(stats)
    
    # Sample rows
    sample_rows = "Sample data:\n"
    for i, row in df.head(5).iterrows():
        sample_rows += f"Row {i}: {', '.join([f'{col}={val}' for col, val in row.items()])}\n"
    
    # Combine all info
    content = df_info + "\n" + df_stats + "\n" + sample_rows
    
    # Create document metadata
    doc_metadata = {
        "source": "dataframe",
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": ",".join(df.columns.tolist())
    }
    
    # Add additional metadata if provided
    if metadata:
        doc_metadata.update(metadata)
    
    # Create a document with all DataFrame info
    doc = Document(page_content=content, metadata=doc_metadata)
    documents.append(doc)
    
    # Optional: Create additional documents for each column description
    for col in df.columns:
        col_content = f"Column '{col}':\n"
        if pd.api.types.is_numeric_dtype(df[col]):
            col_content += f"Type: numeric\n"
            col_content += f"Min: {df[col].min()}\n"
            col_content += f"Max: {df[col].max()}\n"
            col_content += f"Mean: {df[col].mean()}\n"
            col_content += f"Median: {df[col].median()}\n"
        elif pd.api.types.is_datetime64_dtype(df[col]):
            col_content += f"Type: datetime\n"
            col_content += f"Min: {df[col].min()}\n"
            col_content += f"Max: {df[col].max()}\n"
        else:
            col_content += f"Type: {df[col].dtype}\n"
            if df[col].nunique() < 10:
                col_content += f"Unique values: {', '.join(map(str, df[col].unique()))}\n"
            else:
                col_content += f"Number of unique values: {df[col].nunique()}\n"
        
        col_metadata = {
            "source": "dataframe_column",
            "column_name": col,
            "column_type": str(df[col].dtype)
        }
        
        # Add additional metadata if provided
        if metadata:
            col_metadata.update(metadata)
        
        col_doc = Document(page_content=col_content, metadata=col_metadata)
        documents.append(col_doc)
    
    return documents

# Add DataFrame to vector store
def add_dataframe_to_vectorstore(
    df: pd.DataFrame, 
    vectorstore: Chroma, 
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    metadata: Optional[Dict[str, Any]] = None
) -> Chroma:
    """
    Add DataFrame to vector store
    
    Args:
        df: Pandas DataFrame
        vectorstore: Chroma vector store
        chunk_size: Text chunk size
        chunk_overlap: Text chunk overlap
        metadata: Additional metadata to add to documents
    
    Returns:
        Updated Chroma vector store
    """
    # Create documents from DataFrame
    documents = create_documents_from_dataframe(df, metadata)
    
    # Split documents if they're large
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    splits = text_splitter.split_documents(documents)
    
    # Add to vector store
    vectorstore.add_documents(splits)
    
    return vectorstore

# Function to create vector store from dataset
def create_vectorstore_from_dataset(
    df: pd.DataFrame,
    persist_directory: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Chroma:
    """
    Create a new vector store from a dataset
    
    Args:
        df: Pandas DataFrame
        persist_directory: Directory to persist vector store
        metadata: Additional metadata to add to documents
    
    Returns:
        Chroma vector store
    """
    # Initialize vector store
    vectorstore = init_vector_store(persist_directory)
    
    # Add DataFrame to vector store
    vectorstore = add_dataframe_to_vectorstore(df, vectorstore, metadata=metadata)
    
    # Persist if directory is provided
    if persist_directory:
        vectorstore.persist()
    
    return vectorstore

# Function to search vector store
def search_vectorstore(
    vectorstore: Chroma,
    query: str,
    k: int = 5,
    filter: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """
    Search the vector store for similar documents
    
    Args:
        vectorstore: Chroma vector store
        query: Search query
        k: Number of results to return
        filter: Metadata filter
    
    Returns:
        List of Document objects
    """
    results = vectorstore.similarity_search(query, k=k, filter=filter)
    return results

# Function to get related documents for a query
def get_related_documents(
    vectorstore: Chroma,
    query: str,
    k: int = 5,
    filter: Optional[Dict[str, Any]] = None
) -> List[Document]:
    """
    Get related documents for a query
    
    Args:
        vectorstore: Chroma vector store
        query: Search query
        k: Number of results to return
        filter: Metadata filter
    
    Returns:
        List of Document objects
    """
    return search_vectorstore(vectorstore, query, k, filter)
