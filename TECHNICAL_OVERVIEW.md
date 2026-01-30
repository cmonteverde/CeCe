# Technical Overview: CeCe - Climate Copilot

## 1. Project Overview
**CeCe (Climate Copilot)** is an AI-powered analytics dashboard designed to democratize access to climate data. It combines scientific datasets (NASA, NOAA) with Generative AI (OpenAI) to provide actionable insights, visualizations, and resilience strategies for various industries (Agriculture, Energy, Insurance, etc.).

## 2. Architecture
The application is built as a monolithic **Streamlit** web application (`app.py`). It relies on a set of modular Python scripts for data fetching, processing, and visualization.

*   **Frontend:** Streamlit (Python-based UI).
*   **Visualization:** Folium (interactive maps), Plotly (charts), PyDeck (3D maps).
*   **Backend Logic:** Python modules for API interaction and data processing.
*   **AI Engine:** OpenAI GPT-4o (via `openai` library).

## 3. Key Modules & Components

### Core Application
*   **`app.py`**: The main entry point. It handles the UI layout, state management (`st.session_state`), and routing between different features (e.g., "Precipitation Map", "Climate Story").

### Data Integration
*   **`nasa_data.py`**: The primary engine for meteorological data.
    *   **Source:** NASA POWER API (`https://power.larc.nasa.gov`).
    *   **Functions:** `fetch_nasa_power_data`, `fetch_precipitation_map_data`, `get_temperature_trends`.
    *   **Features:** Caching (custom dictionary implementation), interpolation for maps.
*   **`climate_data_sources.py`**: Handles global climate indicators.
    *   **Sources:** NOAA NCEI (Global Temp), NOAA GML (CO2), CSIRO (Sea Level).
    *   **Method:** direct CSV downloads and parsing.
*   **`noaa_nws.py`** (New/Planned): Integration with the National Weather Service API for real-time alerts and forecasts.

### Analytics & AI
*   **`climate_resilience.py`**: Generates industry-specific risk reports (e.g., crop yield risks for Agriculture) based on climate projections (RCP scenarios).
*   **`climate_story_generator.py`**: Uses GPT-4o to craft narrative stories (Personal, Educational, Historical) based on raw data insights.
*   **`openai_helper.py`**: Wrapper for OpenAI interactions with retry logic and system prompts.

### Visualization Helpers
*   **`simple_artistic_maps.py`**: Generates stylized static maps.
*   **`simple_contour_map.py`**: Interactive terrain visualization.
*   **`embedded_earth_nullschool.py`**: Integrates the "earth.nullschool.net" wind visualization.

## 4. Data Sources & APIs

| Source | Type | Usage | Status |
| :--- | :--- | :--- | :--- |
| **NASA POWER** | API (REST) | Daily weather data (Temp, Precip, Wind, Humidity) for any lat/lon. | ✅ Active |
| **NOAA NCEI** | CSV (HTTP) | Historical global temperature anomalies (1880-Present). | ✅ Active |
| **NOAA GML** | CSV (HTTP) | Atmospheric CO2 concentrations (Mauna Loa). | ✅ Active |
| **CSIRO** | CSV (HTTP) | Global Mean Sea Level rise data. | ✅ Active |
| **OpenAI** | API | Chat interface, story generation, and insight synthesis. | ✅ Active |
| **Nominatim** | API | Geocoding (City name to Lat/Lon). | ✅ Active |
| **NOAA NWS** | API (REST) | Real-time US weather alerts and forecasts. | ✅ Active |

## 5. Best Practices & Roadmap Recommendations

To further enhance the application, the following APIs and practices are recommended:

### Recommended APIs
1.  **Open-Meteo:**
    *   *Why:* Extremely fast, free, no-key API for global weather (historical & forecast). Good fallback or alternative to NASA POWER for non-US locations.
2.  **OpenAQ:**
    *   *Why:* Best open source for real-time Air Quality Index (AQI) and pollutants (PM2.5, NO2).
3.  **Sentinel Hub / Landsat (via USGS):**
    *   *Why:* Real satellite imagery for "Artistic Maps" instead of synthetic/generated ones.

### Codebase Improvements
*   **Asynchronous Data Fetching:** Use `asyncio` and `aiohttp` for fetching data for maps to improve UI responsiveness (currently uses sequential or threaded requests).
*   **Type Hinting:** Add Python type hints (`def func(a: int) -> str:`) to all modules for better maintainability.
*   **Configuration Management:** Move all API URLs and configuration constants to a `config.py` file or `st.secrets`.
