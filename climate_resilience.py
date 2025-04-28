"""
Climate Resilience Prediction Module

This module provides predictive modeling and adaptive strategy suggestions 
for various industries based on projected climate scenarios.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import NASA data module for climate projections
import nasa_data

# Climate scenario definitions with industry-specific impacts
CLIMATE_SCENARIOS = {
    "optimistic": {
        "name": "Optimistic Scenario (RCP 2.6)",
        "description": "Limited warming scenario with global temperature increase of 0.9-2.3°C by 2100.",
        "temperature_change_range": [0.9, 2.3],
        "precipitation_change_range": [-5, 10],  # Percent change
        "extreme_events_multiplier": 1.5,
        "sea_level_rise_range": [0.3, 0.6],  # In meters
        "industry_impacts": {
            "aerospace": {
                "severity": "low",
                "impact_areas": [
                    "Slight increases in clear-air turbulence",
                    "Minor changes to optimal flight paths",
                    "Small increases in weather delays"
                ]
            },
            "agriculture": {
                "severity": "moderate",
                "impact_areas": [
                    "Growing season changes of 5-15 days",
                    "Crop yield variations of ±10%",
                    "Minimal water stress in most regions"
                ]
            },
            "energy": {
                "severity": "low",
                "impact_areas": [
                    "Small increases in cooling demand",
                    "Minor reductions in heating demand",
                    "Limited impact on renewable generation potential"
                ]
            },
            "insurance": {
                "severity": "moderate",
                "impact_areas": [
                    "10-25% increase in weather-related claims",
                    "Moderate coastal property risk increases",
                    "Limited expansion of high-risk zones"
                ]
            },
            "forestry": {
                "severity": "moderate",
                "impact_areas": [
                    "Minor shifts in species distribution",
                    "Moderate increase in fire risk in some regions",
                    "Limited pest and disease pressure changes"
                ]
            },
            "catastrophes": {
                "severity": "moderate",
                "impact_areas": [
                    "25-40% increase in major hurricane frequency",
                    "Limited expansion of flood zones",
                    "Moderate increase in drought frequency"
                ]
            }
        }
    },
    "moderate": {
        "name": "Moderate Scenario (RCP 4.5)",
        "description": "Intermediate scenario with global temperature increase of 1.7-3.2°C by 2100.",
        "temperature_change_range": [1.7, 3.2],
        "precipitation_change_range": [-10, 15],  # Percent change
        "extreme_events_multiplier": 2.2,
        "sea_level_rise_range": [0.5, 0.9],  # In meters
        "industry_impacts": {
            "aerospace": {
                "severity": "moderate",
                "impact_areas": [
                    "Moderate increases in turbulence intensity and frequency",
                    "Notable changes to optimal flight routes",
                    "Increased airport disruptions from weather events"
                ]
            },
            "agriculture": {
                "severity": "high",
                "impact_areas": [
                    "Growing season changes of 15-30 days",
                    "Crop yield variations of ±20-25%",
                    "Moderate water stress in many agricultural regions"
                ]
            },
            "energy": {
                "severity": "moderate",
                "impact_areas": [
                    "20-35% increases in cooling demand",
                    "15-25% reductions in heating demand",
                    "Moderate impacts on hydropower generation"
                ]
            },
            "insurance": {
                "severity": "high",
                "impact_areas": [
                    "40-75% increase in weather-related claims",
                    "Significant coastal property risk increases",
                    "Substantial expansion of high-risk zones"
                ]
            },
            "forestry": {
                "severity": "high",
                "impact_areas": [
                    "Moderate shifts in species distribution and growth rates",
                    "60-90% increase in wildfire frequency in vulnerable regions",
                    "Significant increases in pest outbreaks"
                ]
            },
            "catastrophes": {
                "severity": "high",
                "impact_areas": [
                    "50-80% increase in major hurricane frequency",
                    "Significant expansion of flood zones",
                    "High increase in drought frequency and intensity"
                ]
            }
        }
    },
    "severe": {
        "name": "Severe Scenario (RCP 8.5)",
        "description": "High emissions scenario with global temperature increase of 3.2-5.4°C by 2100.",
        "temperature_change_range": [3.2, 5.4],
        "precipitation_change_range": [-20, 25],  # Percent change
        "extreme_events_multiplier": 4.0,
        "sea_level_rise_range": [0.8, 1.5],  # In meters
        "industry_impacts": {
            "aerospace": {
                "severity": "high",
                "impact_areas": [
                    "Severe increases in turbulence frequency and intensity",
                    "Major disruptions to standard flight paths",
                    "Frequent airport closures due to extreme weather"
                ]
            },
            "agriculture": {
                "severity": "severe",
                "impact_areas": [
                    "Growing season changes of 30-60+ days",
                    "Crop yield reductions of 25-50% in many regions",
                    "Severe water stress and irrigation challenges"
                ]
            },
            "energy": {
                "severity": "high",
                "impact_areas": [
                    "50-100% increases in cooling demand",
                    "30-45% reductions in heating demand",
                    "Severe impacts on hydropower from changed precipitation patterns"
                ]
            },
            "insurance": {
                "severity": "severe",
                "impact_areas": [
                    "100-200% increase in weather-related claims",
                    "Uninsurable zones in coastal and high-risk areas",
                    "Catastrophic impacts on property values in vulnerable regions"
                ]
            },
            "forestry": {
                "severity": "severe",
                "impact_areas": [
                    "Major shifts in species distribution with local extinctions",
                    "150-300% increase in wildfire frequency and intensity",
                    "Widespread forest mortality from multiple stressors"
                ]
            },
            "catastrophes": {
                "severity": "severe",
                "impact_areas": [
                    "100-150% increase in major hurricane frequency and intensity",
                    "Extreme expansion of flood zones and flood severity",
                    "Unprecedented drought duration and intensity"
                ]
            }
        }
    }
}

# Adaptive strategies database for each industry and impact severity level
ADAPTIVE_STRATEGIES = {
    "aerospace": {
        "low": [
            "Implement enhanced weather monitoring systems",
            "Optimize flight paths based on seasonal climate predictions",
            "Develop limited turbulence avoidance protocols"
        ],
        "moderate": [
            "Invest in aircraft upgrades for improved turbulence handling",
            "Develop dynamic flight path adjustments based on real-time climate data",
            "Enhance airport infrastructure for increased weather resilience",
            "Implement advanced de-icing capabilities"
        ],
        "high": [
            "Major redesign of flight routes and schedules based on climate projections",
            "Significant infrastructure hardening at vulnerable airports",
            "Development of new aircraft designs optimized for turbulence and extreme weather",
            "Implementation of AI-driven adaptive flight planning systems",
            "Creation of strategic airport climate resilience plans"
        ],
        "severe": [
            "Complete transformation of aviation operations in high-risk regions",
            "Implementation of revolutionary aircraft designs for extreme conditions",
            "Development of alternative transportation systems for high-disruption routes",
            "Comprehensive climate-adaptive airport redesigns",
            "Major investments in predictive weather technology and infrastructure"
        ]
    },
    "agriculture": {
        "low": [
            "Gradual introduction of drought-resistant crop varieties",
            "Minor adjustments to planting and harvesting schedules",
            "Implementation of basic water conservation measures"
        ],
        "moderate": [
            "Transition to climate-adapted crop varieties in vulnerable regions",
            "Significant adjustments to planting calendars based on growing degree days",
            "Implementation of enhanced irrigation efficiency systems",
            "Development of diversified cropping systems",
            "Expanded crop insurance programs"
        ],
        "high": [
            "Large-scale transition to climate-resilient crops and farming systems",
            "Implementation of precision agriculture and advanced irrigation technologies",
            "Development of heat and drought early warning systems",
            "Creation of strategic water storage infrastructure",
            "Implementation of agroforestry and other resilient farming practices"
        ],
        "severe": [
            "Transformation to novel farming systems designed for extreme conditions",
            "Widespread implementation of protected agriculture (greenhouses, vertical farms)",
            "Major investment in desalination and water recycling systems",
            "Development of alternative food production systems",
            "Relocation of agricultural production to newly viable regions"
        ]
    },
    "energy": {
        "low": [
            "Gradual upgrades to grid infrastructure",
            "Increased maintenance schedules during extreme weather seasons",
            "Limited diversification of energy sources"
        ],
        "moderate": [
            "Significant hardening of vulnerable grid infrastructure",
            "Moderate expansion of renewable energy capacity",
            "Development of energy storage solutions",
            "Implementation of demand management systems",
            "Strategic undergrounding of critical transmission lines"
        ],
        "high": [
            "Major grid modernization and decentralization",
            "Large-scale renewable energy integration with storage",
            "Comprehensive facility hardening against extreme weather",
            "Development of climate-resilient cooling systems for power plants",
            "Implementation of microgrids in vulnerable regions"
        ],
        "severe": [
            "Complete transformation to distributed and climate-resilient energy systems",
            "Massive expansion of energy storage capacity",
            "Relocation of critical infrastructure from high-risk zones",
            "Development of revolutionary cooling technologies for power generation",
            "Implementation of AI-driven grid management and prediction systems"
        ]
    },
    "insurance": {
        "low": [
            "Gradual adjustments to premium structures in vulnerable regions",
            "Enhanced catastrophe modeling",
            "Development of early warning systems for policyholders"
        ],
        "moderate": [
            "Significant revision of risk models incorporating climate projections",
            "Development of innovative risk-sharing structures",
            "Implementation of parametric insurance products",
            "Creation of incentive programs for property hardening",
            "Strategic withdrawal from highest risk zones"
        ],
        "high": [
            "Major transition to climate-adaptive insurance models",
            "Public-private partnerships for high-risk coverage",
            "Implementation of real-time risk monitoring systems",
            "Development of mandatory climate resilience standards for coverage",
            "Creation of specialized products for climate adaptation financing"
        ],
        "severe": [
            "Fundamental restructuring of property insurance markets",
            "Government backstop programs for uninsurable regions",
            "Implementation of community-based insurance models",
            "Development of managed retreat financing mechanisms",
            "Creation of novel insurance instruments for catastrophic climate risks"
        ]
    },
    "forestry": {
        "low": [
            "Gradual introduction of heat and drought-tolerant tree species",
            "Enhanced forest fire monitoring and prevention",
            "Limited modifications to forest management practices"
        ],
        "moderate": [
            "Significant shifts in species composition in vulnerable forests",
            "Implementation of enhanced fire breaks and access routes",
            "Development of pest and disease early warning systems",
            "Creation of strategic fuel reduction programs",
            "Adjustments to harvesting schedules and methods"
        ],
        "high": [
            "Large-scale transition to climate-adapted forest species",
            "Implementation of assisted migration for vulnerable species",
            "Development of comprehensive fire management infrastructure",
            "Creation of forest landscape connectivity corridors",
            "Major investments in forest health monitoring systems"
        ],
        "severe": [
            "Transformation to novel forest ecosystems and management systems",
            "Implementation of revolutionary fire suppression technologies",
            "Development of engineered forest systems for extreme conditions",
            "Creation of ex-situ conservation for threatened species",
            "Strategic conversion of high-risk forest areas to alternative land uses"
        ]
    },
    "catastrophes": {
        "low": [
            "Enhanced disaster response planning",
            "Improved early warning systems",
            "Limited infrastructure hardening in vulnerable areas"
        ],
        "moderate": [
            "Significant upgrades to evacuation routes and systems",
            "Implementation of building code updates for climate resilience",
            "Development of community resilience hubs",
            "Creation of enhanced flood control infrastructure",
            "Implementation of heat emergency response systems"
        ],
        "high": [
            "Major infrastructure redesign and hardening",
            "Implementation of transformative flood management systems",
            "Development of permanent evacuation zones",
            "Creation of strategic retreat plans for highest-risk areas",
            "Investments in breakthrough emergency response technologies"
        ],
        "severe": [
            "Fundamental transformation of urban design in vulnerable regions",
            "Implementation of revolutionary protective infrastructure",
            "Development of planned relocation strategies from highest-risk zones",
            "Creation of autonomous disaster response systems",
            "Establishment of permanent evacuation zones and alternative settlement areas"
        ]
    }
}

def get_climate_projections(lat, lon, target_year=2050, scenario="moderate"):
    """
    Get climate projections for a specific location and future year
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        target_year: Year for the projection (2030-2100)
        scenario: Climate scenario to use ("optimistic", "moderate", "severe")
    
    Returns:
        Dictionary with climate projections
    """
    if scenario not in CLIMATE_SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}. Use 'optimistic', 'moderate', or 'severe'.")
    
    if target_year < 2030 or target_year > 2100:
        raise ValueError("Target year must be between 2030 and 2100")
    
    # Get historical data for the location to use as a baseline
    current_year = datetime.now().year
    years_ahead = target_year - current_year
    
    # Ensure we have a minimum of 5 years of historical data for baseline
    baseline_start = (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")
    baseline_end = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Get historical temperature data
        baseline_temps = nasa_data.get_temperature_trends(lat, lon, baseline_start, baseline_end)
        
        # Extract basic metrics
        if isinstance(baseline_temps, tuple) and len(baseline_temps) > 0:
            baseline_temps_df = baseline_temps[0]
            baseline_temp = baseline_temps_df['Temperature (°C)'].mean() if 'Temperature (°C)' in baseline_temps_df else 15.0
            baseline_temp_max = baseline_temps_df['Max Temperature (°C)'].mean() if 'Max Temperature (°C)' in baseline_temps_df else baseline_temp + 5.0
            baseline_temp_min = baseline_temps_df['Min Temperature (°C)'].mean() if 'Min Temperature (°C)' in baseline_temps_df else baseline_temp - 5.0
        else:
            # Fallback to reasonable values if data fetch fails
            baseline_temp = 15.0
            baseline_temp_max = 20.0
            baseline_temp_min = 10.0
        
        # Get historical precipitation data
        try:
            # Create a previous year comparison to get precipitation data
            prev_year_start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            prev_year_end = datetime.now().strftime("%Y-%m-%d")
            current_precip, prev_precip = nasa_data.get_rainfall_comparison(
                lat, lon, baseline_start, baseline_end, prev_year_start, prev_year_end)
            baseline_precip = current_precip['Precipitation (mm)'].mean() if 'Precipitation (mm)' in current_precip else 50.0
        except Exception:
            baseline_precip = 50.0  # Fallback value
        
        # Get scenario parameters
        scenario_data = CLIMATE_SCENARIOS[scenario]
        
        # Apply climate scenario to baseline data
        # Scale changes based on how far into the future we're projecting 
        # (more pronounced changes further into future)
        scaling_factor = min(1.0, years_ahead / 80)  # 80 years from now is 2100
        
        # Get lower and upper bounds of the parameters
        temp_change_min, temp_change_max = scenario_data["temperature_change_range"]
        precip_change_min, precip_change_max = scenario_data["precipitation_change_range"]
        slr_min, slr_max = scenario_data["sea_level_rise_range"]
        
        # Calculate projected values with some variability
        temp_change = (temp_change_min + (temp_change_max - temp_change_min) * np.random.random()) * scaling_factor
        precip_change_pct = (precip_change_min + (precip_change_max - precip_change_min) * np.random.random()) * scaling_factor
        extreme_events_factor = 1.0 + (scenario_data["extreme_events_multiplier"] - 1.0) * scaling_factor
        sea_level_rise = (slr_min + (slr_max - slr_min) * np.random.random()) * scaling_factor
        
        # Create projection results
        projected_temp = baseline_temp + temp_change
        projected_temp_max = baseline_temp_max + temp_change * 1.2  # Max temps rise faster
        projected_temp_min = baseline_temp_min + temp_change * 0.8  # Min temps rise slower
        projected_precip = baseline_precip * (1 + precip_change_pct/100)
        
        # Create seasons data with different change patterns
        seasons_temp_change = {
            "winter": temp_change * (0.8 + 0.4 * np.random.random()),  # Winter warming can vary
            "spring": temp_change * (0.9 + 0.2 * np.random.random()),
            "summer": temp_change * (1.1 + 0.3 * np.random.random()),  # Summer warming often more pronounced
            "fall": temp_change * (0.9 + 0.2 * np.random.random())
        }
        
        seasons_precip_change = {
            "winter": precip_change_pct * (1.1 + 0.4 * np.random.random()),  # Winter precipitation often increases more
            "spring": precip_change_pct * (1.0 + 0.3 * np.random.random()),
            "summer": precip_change_pct * (0.7 + 0.6 * np.random.random()),  # Summer can see bigger decreases
            "fall": precip_change_pct * (0.9 + 0.3 * np.random.random())
        }
        
        # Extreme weather projections
        extreme_heat_days_factor = extreme_events_factor * (1.2 + 0.4 * np.random.random())  # Heat extremes rise faster
        extreme_precipitation_factor = extreme_events_factor * (1.1 + 0.3 * np.random.random())
        drought_risk_factor = extreme_events_factor * (0.9 + 0.5 * np.random.random())
        
        return {
            "scenario": scenario,
            "scenario_name": scenario_data["name"],
            "scenario_description": scenario_data["description"],
            "target_year": target_year,
            "temperature": {
                "baseline": round(baseline_temp, 1),
                "projected": round(projected_temp, 1),
                "change": round(temp_change, 1),
                "max": {
                    "baseline": round(baseline_temp_max, 1),
                    "projected": round(projected_temp_max, 1)
                },
                "min": {
                    "baseline": round(baseline_temp_min, 1),
                    "projected": round(projected_temp_min, 1)
                },
                "seasonal_changes": {season: round(change, 1) for season, change in seasons_temp_change.items()}
            },
            "precipitation": {
                "baseline": round(baseline_precip, 1),
                "projected": round(projected_precip, 1),
                "change_percent": round(precip_change_pct, 1),
                "seasonal_changes": {season: round(change, 1) for season, change in seasons_precip_change.items()}
            },
            "extreme_weather": {
                "heat_days_multiplier": round(extreme_heat_days_factor, 1),
                "precipitation_events_multiplier": round(extreme_precipitation_factor, 1),
                "drought_risk_multiplier": round(drought_risk_factor, 1)
            },
            "sea_level_rise": round(sea_level_rise, 2)  # In meters
        }
        
    except Exception as e:
        # If we can't get real data, return a simulated projection
        print(f"Error fetching climate data: {str(e)}")
        print("Using simulated climate projection")
        
        # Get scenario parameters
        scenario_data = CLIMATE_SCENARIOS[scenario]
        
        # Apply climate scenario
        scaling_factor = min(1.0, years_ahead / 80)
        
        # Get middle of the ranges
        temp_change = ((scenario_data["temperature_change_range"][0] + scenario_data["temperature_change_range"][1]) / 2) * scaling_factor
        precip_change_pct = ((scenario_data["precipitation_change_range"][0] + scenario_data["precipitation_change_range"][1]) / 2) * scaling_factor
        extreme_events_factor = 1.0 + (scenario_data["extreme_events_multiplier"] - 1.0) * scaling_factor
        sea_level_rise = ((scenario_data["sea_level_rise_range"][0] + scenario_data["sea_level_rise_range"][1]) / 2) * scaling_factor
        
        return {
            "scenario": scenario,
            "scenario_name": scenario_data["name"],
            "scenario_description": scenario_data["description"],
            "target_year": target_year,
            "temperature": {
                "baseline": 15.0,
                "projected": 15.0 + temp_change,
                "change": temp_change,
                "max": {
                    "baseline": 20.0,
                    "projected": 20.0 + temp_change * 1.2
                },
                "min": {
                    "baseline": 10.0,
                    "projected": 10.0 + temp_change * 0.8
                },
                "seasonal_changes": {
                    "winter": temp_change * 0.9,
                    "spring": temp_change * 1.0, 
                    "summer": temp_change * 1.2,
                    "fall": temp_change * 1.0
                }
            },
            "precipitation": {
                "baseline": 50.0,
                "projected": 50.0 * (1 + precip_change_pct/100),
                "change_percent": precip_change_pct,
                "seasonal_changes": {
                    "winter": precip_change_pct * 1.2,
                    "spring": precip_change_pct * 1.0,
                    "summer": precip_change_pct * 0.7,
                    "fall": precip_change_pct * 1.0
                }
            },
            "extreme_weather": {
                "heat_days_multiplier": extreme_events_factor * 1.3,
                "precipitation_events_multiplier": extreme_events_factor * 1.2,
                "drought_risk_multiplier": extreme_events_factor * 1.1
            },
            "sea_level_rise": sea_level_rise
        }

def get_industry_impact_assessment(industry, projections):
    """
    Assess the impact of climate projections on a specific industry
    
    Args:
        industry: Industry name (aerospace, agriculture, energy, insurance, forestry, catastrophes)
        projections: Climate projection data from get_climate_projections
    
    Returns:
        Dictionary with impact assessment
    """
    if industry not in ADAPTIVE_STRATEGIES:
        raise ValueError(f"Unknown industry: {industry}")
    
    scenario = projections["scenario"]
    scenario_data = CLIMATE_SCENARIOS[scenario]
    industry_impacts = scenario_data["industry_impacts"][industry]
    
    # Get the baseline impact severity from the scenario
    impact_severity = industry_impacts["severity"]
    impact_areas = industry_impacts["impact_areas"]
    
    # Adjust severity based on specifics of the projection
    # This allows for variation within a scenario based on location-specific factors
    severity_adjustment = 0
    
    # Adjust based on temperature change magnitude
    if projections["temperature"]["change"] > scenario_data["temperature_change_range"][1] * 0.8:
        severity_adjustment += 1
    elif projections["temperature"]["change"] < scenario_data["temperature_change_range"][0] * 1.2:
        severity_adjustment -= 1
    
    # Adjust based on precipitation change
    if abs(projections["precipitation"]["change_percent"]) > abs(scenario_data["precipitation_change_range"][1] * 0.8):
        severity_adjustment += 1
    elif abs(projections["precipitation"]["change_percent"]) < abs(scenario_data["precipitation_change_range"][0] * 1.2):
        severity_adjustment -= 1
    
    # Adjust based on extreme weather factors
    extreme_events_baseline = scenario_data["extreme_events_multiplier"]
    extreme_heat_factor = projections["extreme_weather"]["heat_days_multiplier"]
    extreme_precip_factor = projections["extreme_weather"]["precipitation_events_multiplier"]
    
    if (extreme_heat_factor + extreme_precip_factor) / 2 > extreme_events_baseline * 1.1:
        severity_adjustment += 1
    elif (extreme_heat_factor + extreme_precip_factor) / 2 < extreme_events_baseline * 0.9:
        severity_adjustment -= 1
    
    # Industry-specific adjustments
    if industry == "agriculture":
        # Agriculture is very sensitive to seasonal changes
        summer_temp_change = projections["temperature"]["seasonal_changes"]["summer"]
        summer_precip_change = projections["precipitation"]["seasonal_changes"]["summer"]
        
        if summer_temp_change > projections["temperature"]["change"] * 1.2 and summer_precip_change < 0:
            # Hot summers with less rain is particularly bad for agriculture
            severity_adjustment += 1
        
        # Drought risk is critical for agriculture
        if projections["extreme_weather"]["drought_risk_multiplier"] > extreme_events_baseline * 1.1:
            severity_adjustment += 1
    
    elif industry == "energy":
        # Energy is sensitive to extreme heat (grid stress) and precipitation changes (hydropower)
        if extreme_heat_factor > extreme_events_baseline * 1.2:
            severity_adjustment += 1
        
        # Large precipitation changes affect hydropower
        if abs(projections["precipitation"]["change_percent"]) > 15:
            severity_adjustment += 1
    
    elif industry == "insurance":
        # Insurance is highly sensitive to extreme events and sea level rise
        if projections["sea_level_rise"] > scenario_data["sea_level_rise_range"][1] * 0.9:
            severity_adjustment += 1
            
        if extreme_precip_factor > extreme_events_baseline * 1.2:
            # Flood risk is a major insurance concern
            severity_adjustment += 1
    
    elif industry == "forestry":
        # Forestry is sensitive to temperature, drought, and precipitation
        if projections["extreme_weather"]["drought_risk_multiplier"] > extreme_events_baseline * 1.1:
            severity_adjustment += 1
            
        # Hot, dry conditions increase fire risk
        if projections["temperature"]["change"] > scenario_data["temperature_change_range"][1] * 0.8 and projections["precipitation"]["change_percent"] < 0:
            severity_adjustment += 1
    
    elif industry == "aerospace":
        # Aerospace is sensitive to extreme weather events and wind patterns
        if extreme_heat_factor > extreme_events_baseline * 1.2:
            # Extreme heat affects aircraft performance
            severity_adjustment += 1
    
    elif industry == "catastrophes":
        # Catastrophe management is directly tied to extreme events
        if extreme_heat_factor > extreme_events_baseline * 1.1 or extreme_precip_factor > extreme_events_baseline * 1.1:
            severity_adjustment += 1
            
        if projections["sea_level_rise"] > scenario_data["sea_level_rise_range"][1] * 0.9:
            # Sea level rise increases coastal catastrophe risk
            severity_adjustment += 1
    
    # Map severity level
    severity_levels = ["low", "moderate", "high", "severe"]
    base_severity_index = severity_levels.index(impact_severity)
    
    # Apply adjustment with bounds
    adjusted_severity_index = max(0, min(len(severity_levels) - 1, base_severity_index + severity_adjustment))
    adjusted_severity = severity_levels[adjusted_severity_index]
    
    return {
        "industry": industry,
        "base_severity": impact_severity,
        "adjusted_severity": adjusted_severity,
        "impact_areas": impact_areas,
        "severity_adjustment_factors": {
            "temperature_change": projections["temperature"]["change"],
            "precipitation_change": projections["precipitation"]["change_percent"],
            "extreme_weather_factors": projections["extreme_weather"],
            "sea_level_rise": projections["sea_level_rise"]
        }
    }

def get_adaptive_strategies(industry, impact_assessment):
    """
    Get recommended adaptive strategies for an industry based on impact assessment
    
    Args:
        industry: Industry name
        impact_assessment: Impact assessment from get_industry_impact_assessment
    
    Returns:
        List of recommended adaptive strategies
    """
    if industry not in ADAPTIVE_STRATEGIES:
        raise ValueError(f"Unknown industry: {industry}")
    
    severity = impact_assessment["adjusted_severity"]
    
    # Get strategies for the current severity level
    strategies = ADAPTIVE_STRATEGIES[industry].get(severity, [])
    
    # Add some strategies from the next lower level if available
    severity_levels = ["low", "moderate", "high", "severe"]
    if severity != "low":
        prev_severity = severity_levels[severity_levels.index(severity) - 1]
        prev_strategies = ADAPTIVE_STRATEGIES[industry].get(prev_severity, [])
        
        # Add a subset of strategies from previous level
        if prev_strategies:
            # Add 2-3 strategies from previous level
            import random
            num_to_add = min(len(prev_strategies), random.randint(2, 3))
            additional_strategies = random.sample(prev_strategies, num_to_add)
            strategies = additional_strategies + strategies
    
    return strategies

def generate_resilience_report(lat, lon, industry, target_year=2050, scenario="moderate"):
    """
    Generate a comprehensive climate resilience report for an industry
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        industry: Industry name
        target_year: Target year for projections
        scenario: Climate scenario ("optimistic", "moderate", "severe")
    
    Returns:
        Dictionary with resilience report data
    """
    # Get climate projections
    projections = get_climate_projections(lat, lon, target_year, scenario)
    
    # Assess industry impacts
    impact_assessment = get_industry_impact_assessment(industry, projections)
    
    # Get adaptive strategies
    strategies = get_adaptive_strategies(industry, impact_assessment)
    
    # Generate key metrics for visualization
    key_metrics = {
        "temperature_increase": projections["temperature"]["change"],
        "precipitation_change": projections["precipitation"]["change_percent"],
        "extreme_weather_factor": (projections["extreme_weather"]["heat_days_multiplier"] + 
                                  projections["extreme_weather"]["precipitation_events_multiplier"]) / 2,
        "sea_level_rise": projections["sea_level_rise"],
        "impact_severity_score": ["low", "moderate", "high", "severe"].index(impact_assessment["adjusted_severity"]) + 1
    }
    
    # Generate a timeline of recommended implementation
    # Near-term (1-5 years), mid-term (5-15 years), long-term (15+ years)
    implementation_timeline = {
        "near_term": [],
        "mid_term": [],
        "long_term": []
    }
    
    # Distribute strategies across timeline based on complexity and urgency
    if strategies:
        # More severe impacts need more urgent action
        severity_levels = ["low", "moderate", "high", "severe"]
        severity_index = severity_levels.index(impact_assessment["adjusted_severity"])
        
        # Determine distribution based on severity
        if severity_index <= 1:  # low or moderate
            # More balanced distribution
            near_term_count = max(1, len(strategies) // 4)
            mid_term_count = max(1, len(strategies) // 3)
        else:  # high or severe
            # More front-loaded distribution
            near_term_count = max(2, len(strategies) // 3)
            mid_term_count = max(1, len(strategies) // 3)
        
        # Ensure we don't exceed the total count
        long_term_count = len(strategies) - near_term_count - mid_term_count
        
        # Distribute strategies
        implementation_timeline["near_term"] = strategies[:near_term_count]
        implementation_timeline["mid_term"] = strategies[near_term_count:near_term_count+mid_term_count]
        implementation_timeline["long_term"] = strategies[near_term_count+mid_term_count:]
    
    # Determine cost implications based on severity and strategies
    cost_levels = ["low", "moderate", "high", "transformative"]
    severity_levels = ["low", "moderate", "high", "severe"]
    base_cost_index = min(severity_levels.index(impact_assessment["adjusted_severity"]), len(cost_levels) - 1)
    
    # Adjust for number of strategies
    strategy_count_adjustment = 0
    if len(strategies) > 10:
        strategy_count_adjustment = 1
    elif len(strategies) < 5:
        strategy_count_adjustment = -1
    
    cost_index = max(0, min(len(cost_levels) - 1, base_cost_index + strategy_count_adjustment))
    cost_implication = cost_levels[cost_index]
    
    # Build full report
    report = {
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "industry": industry,
        "target_year": target_year,
        "scenario": projections["scenario_name"],
        "climate_projections": projections,
        "impact_assessment": impact_assessment,
        "adaptive_strategies": strategies,
        "implementation_timeline": implementation_timeline,
        "cost_implication": cost_implication,
        "key_metrics": key_metrics
    }
    
    return report