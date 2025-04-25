# Climate Copilot – Product Requirements Document (PRD)

## 📌 Overview

**Product Name:** Climate Copilot  
**Version:** Prototype v0.1  
**Author:** Corrie Monteverde  
**Last Updated:** April 1, 2025  

**Purpose:**  
The Climate Copilot is an AI-powered assistant that helps users seamlessly interact with climate and weather data. It simplifies complex scientific workflows into a user-friendly interface for planners, researchers, and practitioners across sectors.

## 🎯 Core Functionality

- Upload and preview climate/weather datasets (CSV, NASA POWER API)
- Perform scientific calculations (e.g., temperature anomalies, GDD, PET)
- Visualize data through charts and maps
- Chat with datasets using LLM + LangChain RAG architecture
- Export transformed datasets and visualizations (CSV, PNG, GeoJSON)
- Allow user login (Auth0 integration)
- Save and download session chat history

## 🧭 User Flows

### 1. Data Upload
- Upload local file or fetch from NASA POWER API
- Validate and preview dataset in tabular view

### 2. Clean & Preview
- Show column stats, allow dropping or filtering
- Date-based filtering (if time series)

### 3. Visualize
- Select X/Y axis
- Plot line, bar, or scatter graphs
- For geospatial: render Folium map

### 4. Calculations
- Choose scientific calculation from dropdown
- Input required columns (e.g., TMAX, RH)
- Run transformation, preview result, download as CSV

### 5. Chat with Data
- Ask natural language questions
- Query response generated using DeepSeek + LangChain + Chroma
- Save full chat history and allow export

### 6. Export
- Select data format: CSV, PNG, GeoJSON
- Trigger download from UI

### 7. Settings
- Switch LLM provider (DeepSeek, OpenAI)
- Input tokens (Auth0, NASA API)
- Toggle units and app preferences

## 🚨 Critical Requirements

- **LLM Backend**: DeepSeek-V3 via Hugging Face API
- **Vector DB**: ChromaDB
- **Frontend**: Streamlit with modular page-based navigation
- **Calculation Module**: `climate_algorithms.py` with reusable scientific formulas
- **Auth**: Auth0 login integration (email, Google)
- **Session Storage**: All calculations and chat should persist per user session

## 📁 File & Directory Structure

```
climate_agent/
├── app.py
├── rag_query.py
├── transform.py
├── climate_algorithms.py
├── auth.py
├── vector_store.py
├── load_docs.py
├── .env
└── README.md
```

## ✅ Success Criteria

- Prototype is deployed and working in Replit or local dev
- User can run at least 2 calculations and generate visualizations
- Chat with data returns relevant responses based on uploaded file
- NASA API integration returns real data and stores it in session
- User can export processed file and chat transcript