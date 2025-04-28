"""
Climate Story Generator Module

This module transforms climate data into personalized, narrative-driven stories
that make environmental insights more engaging and memorable. It uses AI to generate
context-rich, educational stories based on climate data from the user's location.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import openai
import json

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None

def generate_climate_story(data, location, timeframe, story_type="personal"):
    """
    Generate a personalized climate story based on data and location
    
    Args:
        data: DataFrame containing climate data
        location: Dictionary with location info (city name, lat, lon)
        timeframe: Dictionary with timeframe info (start_date, end_date)
        story_type: Type of story to generate (personal, educational, historical)
    
    Returns:
        Dictionary containing the story components (text, insights, visualization_suggestions)
    """
    # Ensure we have an OpenAI API key
    if not client:
        return {
            "text": "Unable to generate climate story: OpenAI API key not found.",
            "insights": [],
            "visualization_suggestions": []
        }
    
    # Process the data to extract key insights
    insights = extract_climate_insights(data)
    
    # Create a prompt for the story generation
    location_str = location.get("city", f"{location['lat']:.4f}°, {location['lon']:.4f}°")
    start_date = timeframe["start_date"].strftime('%Y-%m-%d') if isinstance(timeframe["start_date"], datetime) else timeframe["start_date"]
    end_date = timeframe["end_date"].strftime('%Y-%m-%d') if isinstance(timeframe["end_date"], datetime) else timeframe["end_date"]
    
    # Different prompt templates based on story type
    if story_type == "personal":
        prompt = generate_personal_story_prompt(insights, location_str, start_date, end_date)
    elif story_type == "educational":
        prompt = generate_educational_story_prompt(insights, location_str, start_date, end_date)
    elif story_type == "historical":
        prompt = generate_historical_story_prompt(insights, location_str, start_date, end_date)
    else:
        prompt = generate_personal_story_prompt(insights, location_str, start_date, end_date)
    
    # Generate the story using OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the newest OpenAI model "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a creative climate storyteller who transforms climate data into engaging, educational narratives."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        story_result = json.loads(response.choices[0].message.content)
        return story_result
        
    except Exception as e:
        return {
            "text": f"Error generating climate story: {str(e)}",
            "insights": insights,
            "visualization_suggestions": []
        }

def extract_climate_insights(data):
    """
    Extract key insights from climate data
    
    Args:
        data: DataFrame containing climate data
    
    Returns:
        List of insights with descriptive text
    """
    insights = []
    
    # Skip if data is empty or None
    if data is None or len(data) == 0:
        return insights
    
    try:
        # Temperature insights
        if 'T2M' in data.columns:
            avg_temp = data['T2M'].mean()
            max_temp = data['T2M'].max()
            min_temp = data['T2M'].min()
            temp_range = max_temp - min_temp
            
            insights.append(f"The average temperature was {avg_temp:.1f}°C")
            insights.append(f"The highest temperature recorded was {max_temp:.1f}°C")
            insights.append(f"The lowest temperature recorded was {min_temp:.1f}°C")
            insights.append(f"The temperature varied by {temp_range:.1f}°C during this period")
        
        # Precipitation insights
        if 'PRECTOTCORR' in data.columns:
            total_precip = data['PRECTOTCORR'].sum()
            rainy_days = (data['PRECTOTCORR'] > 1.0).sum()  # Days with more than 1mm rain
            max_precip = data['PRECTOTCORR'].max()
            
            insights.append(f"Total precipitation was {total_precip:.1f}mm")
            insights.append(f"There were {rainy_days} days with significant rainfall")
            insights.append(f"The maximum daily precipitation was {max_precip:.1f}mm")
        
        # Humidity insights
        if 'RH2M' in data.columns:
            avg_humidity = data['RH2M'].mean()
            insights.append(f"The average relative humidity was {avg_humidity:.1f}%")
        
        # Wind insights
        if 'WS2M' in data.columns:
            avg_wind = data['WS2M'].mean()
            max_wind = data['WS2M'].max()
            insights.append(f"The average wind speed was {avg_wind:.1f}m/s")
            insights.append(f"The maximum wind speed was {max_wind:.1f}m/s")
        
        # Trend insights
        if 'T2M' in data.columns and len(data) > 10:
            # Simple linear regression to detect trends
            x = np.arange(len(data))
            y = data['T2M'].values
            slope = np.polyfit(x, y, 1)[0]
            
            trend_direction = "warming" if slope > 0 else "cooling"
            trend_strength = abs(slope * len(data))
            
            if trend_strength > 1:
                insights.append(f"There is a {trend_direction} trend of {trend_strength:.1f}°C over this period")
        
        # Seasonal patterns
        if 'Date' in data.columns and len(data) > 30:
            data['Month'] = pd.to_datetime(data['Date']).dt.month
            monthly_avg = data.groupby('Month')['T2M'].mean() if 'T2M' in data.columns else None
            
            if monthly_avg is not None:
                hottest_month = monthly_avg.idxmax()
                coldest_month = monthly_avg.idxmin()
                month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 
                               6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 
                               11: 'November', 12: 'December'}
                
                insights.append(f"The warmest month was {month_names[hottest_month]} with an average of {monthly_avg[hottest_month]:.1f}°C")
                insights.append(f"The coldest month was {month_names[coldest_month]} with an average of {monthly_avg[coldest_month]:.1f}°C")
    
    except Exception as e:
        insights.append(f"Error extracting insights: {str(e)}")
    
    return insights

def generate_personal_story_prompt(insights, location, start_date, end_date):
    """
    Generate a prompt for a personal climate story
    """
    insights_text = "\n".join([f"- {insight}" for insight in insights])
    
    prompt = f"""
    Create a personalized climate story based on the following data insights for {location} from {start_date} to {end_date}:
    
    {insights_text}
    
    Make the story engaging and first-person, as if the reader experienced these climate conditions. 
    Include sensory details and emotional elements to make the climate data feel real and relatable.
    Educate the reader about these climate patterns while maintaining an engaging narrative.
    
    Format your response as a JSON object with the following structure:
    {{
        "title": "A creative, engaging title for the story",
        "text": "The full story text with multiple paragraphs",
        "insights": ["3-5 key climate insights explained in plain language"],
        "visualization_suggestions": ["2-3 ideas for visualizing this data"]
    }}
    """
    
    return prompt

def generate_educational_story_prompt(insights, location, start_date, end_date):
    """
    Generate a prompt for an educational climate story
    """
    insights_text = "\n".join([f"- {insight}" for insight in insights])
    
    prompt = f"""
    Create an educational climate story based on the following data insights for {location} from {start_date} to {end_date}:
    
    {insights_text}
    
    Frame this as an educational journey exploring climate patterns. Use clear explanations of climate 
    science concepts that would be appropriate for middle or high school students. Connect the local 
    climate patterns to global climate systems.
    
    Format your response as a JSON object with the following structure:
    {{
        "title": "An educational title that captures interest",
        "text": "The full educational story with scientific explanations embedded naturally",
        "insights": ["3-5 key climate science concepts explained simply"],
        "visualization_suggestions": ["2-3 educational visualizations that would help explain these concepts"]
    }}
    """
    
    return prompt

def generate_historical_story_prompt(insights, location, start_date, end_date):
    """
    Generate a prompt for a historical climate story
    """
    insights_text = "\n".join([f"- {insight}" for insight in insights])
    
    prompt = f"""
    Create a historical climate narrative based on the following data insights for {location} from {start_date} to {end_date}:
    
    {insights_text}
    
    Frame this as a historical perspective, comparing these modern climate patterns with how they might 
    have impacted historical societies in this region. Consider how these climate conditions would have 
    affected agriculture, settlement, and daily life throughout human history in this area.
    
    Format your response as a JSON object with the following structure:
    {{
        "title": "A historically-themed title for the climate narrative",
        "text": "The full historical climate narrative with connections to human history",
        "insights": ["3-5 key insights about how climate shaped history in this region"],
        "visualization_suggestions": ["2-3 ideas for visualizations that connect climate data to historical context"]
    }}
    """
    
    return prompt

def generate_visualizations_from_story(data, story):
    """
    Generate visualization suggestions based on the story and data
    
    Args:
        data: DataFrame containing climate data
        story: Dictionary containing the story components
    
    Returns:
        List of visualization descriptions
    """
    # This function would be implemented to generate actual visualization code based on the story
    # For now, we'll just return the visualization suggestions from the story
    return story.get("visualization_suggestions", [])