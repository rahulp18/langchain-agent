 
import os
import httpx
from langchain_core.tools import tool
OPENWEATHER_BASE_URL="https://api.openweathermap.org"
@tool
async def search_weather(city_name:str)->list|dict:
  """
  Get the current weather for a city

  The tool first converts the city name into latitude/longitude 
  using OpenWeather's geocodeing API , then uses those coordinates to fetch the current weather
  """
 
  apiKey=os.getenv('WEATHER_API_KEY')
  if not apiKey:
    return{
      "error":"Weather service is not configured"
    }
  city_name=city_name.strip()
  if not city_name:
    return {
      "error":"City name connot be empty"
    }
 
  async with httpx.AsyncClient() as client:
    try:
      response=await client.get(f"{OPENWEATHER_BASE_URL}/geo/1.0/direct",params={
        "q":city_name,
        "limit":1,
        "appid":apiKey
      })
      response.raise_for_status()
      geo_data= response.json()
      if not geo_data:
        return{
          "error":f"Could not find the city '{city_name}'"
        }
      location=geo_data[0]
      latitude=location['lat'] 
      longitude=location["lon"] 
      resolved_city=location.get(
        "name",
        city_name
      )
      country=location.get("country")
      state=location.get("state")
      weather_response=await client.get(f"{OPENWEATHER_BASE_URL}/data/2.5/weather",params={
        "lat":latitude,
        "lon":longitude,
         "appid":apiKey,
         "units":"metric"
      })
      weather_response.raise_for_status()
      weather_data= weather_response.json()

      main=weather_data.get('main',{})
      weather=weather_data.get("weather",[{}])[0]
      wind=weather_data.get("wind",{})
     
      return {
                "city": resolved_city,
                "state": state,
                "country": country,
                "temperature": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "humidity": main.get("humidity"),
                "condition": weather.get("description"),
                "wind_speed": wind.get("speed"),
            }
    except httpx.TimeoutException:
            return {
                "error": "Weather service timed out. Please try again."
            }

    except httpx.HTTPStatusError as error:

            status_code = error.response.status_code

            if status_code == 401:
                return {
                    "error": "Weather service authentication failed."
                }

            if status_code == 404:
                return {
                    "error": "Weather information was not found."
                }

            return {
                "error": "Weather service returned an HTTP error."
            }

    except httpx.HTTPError:
            return {
                "error": "Could not connect to the weather service."
            }

    except (KeyError, IndexError):
            return {
                "error": "Weather service returned an unexpected response."
            }

    except Exception:
            return {
                "error": "An unexpected error occurred while fetching weather."
            }

