# Climate Copilot (CeCe) - Architecture Overview

## 1. Overview

Climate Copilot (CeCe) is an AI-powered web application designed to help users interact with climate and weather data through a user-friendly interface. The application provides data visualization, scientific calculations, and natural language interaction with climate datasets. It combines real-time climate data retrieval, advanced mapping features, and AI assistance to simplify complex scientific workflows for planners and analysts.

## 2. System Architecture

Climate Copilot follows a single-tier architecture built on Streamlit, with various specialized modules integrating multiple external APIs and data sources. The application is structured around these core capabilities:

1. **Data Retrieval**: Integration with NASA POWER API and Copernicus Climate Data Store (CDS) for climate data
2. **Data Processing**: Scientific calculation modules for climate metrics (GDD, temperature anomalies)
3. **Visualization**: Advanced mapping capabilities with Folium and Plotly
4. **AI Interaction**: OpenAI integration for natural language processing of climate data
5. **Authentication**: Auth0 integration for user authentication

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       Streamlit Web UI                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                               │                                 │
│  ┌─────────────────┐    ┌─────┴──────┐    ┌──────────────────┐  │
│  │     Climate     │    │    Data    │    │   Visualization  │  │
│  │   Algorithms    │    │ Processing │    │      Engine      │  │
│  └─────────────────┘    └─────┬──────┘    └──────────────────┘  │
│                               │                                 │
│  ┌─────────────────┐    ┌─────┴──────┐    ┌──────────────────┐  │
│  │    RAG Query    │    │   Vector   │    │     Maps &       │  │
│  │     Engine      │    │    Store   │    │     Globes       │  │
│  └─────────────────┘    └─────┬──────┘    └──────────────────┘  │
│                               │                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────────┐
│                         External APIs                           │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────┐    ┌──────────────────┐ │
│  │   NASA POWER    │    │   CDS ERA5  │    │      OpenAI      │ │
│  │      API        │    │     API     │    │       API        │ │
│  └─────────────────┘    └─────────────┘    └──────────────────┘ │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────┐                         │
│  │      Auth0      │    │ Earth Engine│                         │
│  │                 │    │   Elevation │                         │
│  └─────────────────┘    └─────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## 3. Key Components

### 3.1 Frontend UI (Streamlit)

- **Technology**: Streamlit
- **Purpose**: Provides an interactive web interface for the application
- **Key Features**:
  - Interactive data visualization
  - Map rendering via Folium integration
  - User input forms and controls
  - Chat interface for AI interaction

### 3.2 Climate Data Processing

- **Core Modules**: 
  - `climate_algorithms.py`: Scientific calculations for climate data
  - `transform.py`: Data transformation and preprocessing
  - `climate_resilience.py`: Predictive modeling for climate scenarios

- **Data Sources**:
  - `nasa_data.py`: Interface for NASA POWER API
  - `era5_data.py`: Interface for Copernicus Climate Data Store (CDS)
  - `climate_data_sources.py`: Generic interface for multiple climate data sources

### 3.3 Map Visualization Engine

- **Core Modules**:
  - `felt_inspired_maps.py`: Modern, interactive map experiences
  - `artistic_maps.py`: Stylized map visualizations
  - `simple_artistic_maps.py`: Simplified map visualizations
  - `globe_map.py`: Interactive 3D globe visualization

- **Features**:
  - Multiple basemap options
  - Climate data overlays
  - Artistic rendering of climate data
  - Interactive controls for map manipulation

### 3.4 AI Components

- **RAG Implementation**:
  - `rag_query.py`: Retrieval-Augmented Generation for climate data queries
  - `vector_store.py`: Vector database for document storage
  - `load_docs.py`: Document loading and processing

- **Story Generation**:
  - `climate_story_generator.py`: Transforms climate data into narrative content

### 3.5 Authentication System

- **Implementation**: Auth0 integration
- **Core Module**: `auth.py`
- **Features**:
  - User login/authentication
  - Session management
  - Secure access control

## 4. Data Flow

### 4.1 Climate Data Acquisition

1. User requests climate data for a specific location and time period
2. Application fetches data from NASA POWER API or CDS ERA5 API
3. Raw data is processed and transformed into a standardized format
4. Processed data is stored in memory for the current session

### 4.2 Data Visualization Flow

1. User selects visualization type (maps, charts, globes)
2. Application passes processed data to the appropriate visualization module
3. Visualization modules render the data using Folium, Plotly, or Matplotlib
4. Rendered visualizations are displayed in the Streamlit UI

### 4.3 AI Interaction Flow

1. User submits a natural language query about climate data
2. Query is processed by the RAG engine
3. RAG engine retrieves relevant information from vector store
4. OpenAI API generates a response based on the retrieved information
5. Response is displayed to the user in the chat interface

## 5. External Dependencies

### 5.1 Cloud Services

- **OpenAI API**: Used for natural language processing and generation
- **Auth0**: Used for authentication and user management
- **Copernicus Climate Data Store (CDS)**: Source for ERA5 climate data
- **NASA POWER API**: Source for climate and meteorological data

### 5.2 Key Python Libraries

- **Streamlit**: Web application framework
- **Folium**: Interactive map visualization
- **Plotly**: Interactive data visualization
- **Pandas/NumPy**: Data processing and analysis
- **Langchain**: (Commented out but intended) Framework for AI applications
- **Chroma**: Vector database for document retrieval

## 6. Deployment Strategy

The application is deployed using Replit's platform, configured with the following specifications:

- **Runtime Environment**: Python 3.11
- **Deployment Target**: Autoscale
- **Run Command**: `streamlit run app.py --server.port 5000`
- **External Port Mapping**: Internal port 5000 mapped to external port 80

### 6.1 Environment Variables

The application relies on several environment variables:
- `OPENAI_API_KEY`: Authentication for OpenAI API
- `CDS_URL` and `CDS_KEY`: Authentication for Copernicus Climate Data Store
- `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`: Auth0 configuration
- `NASA_EE_USERNAME` and `NASA_EE_PASSWORD`: (Optional) NASA Earth Explorer credentials

### 6.2 Scaling Considerations

- The application currently operates as a single instance without database persistence
- Session state is maintained in-memory during user interaction
- For production scaling, implementation of persistent storage would be necessary
- Vector store is currently in-memory but could be persisted for production use

## 7. Future Architecture Considerations

- **Database Integration**: Adding persistent storage for user data and preferences
- **Microservices Architecture**: Splitting the application into specialized services
- **Containerization**: Docker deployment for better environment control and scaling
- **API Layer**: Developing a separate API layer for third-party integrations
- **Caching Layer**: Implementing a caching system for frequently accessed climate data