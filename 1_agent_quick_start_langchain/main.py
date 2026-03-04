from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.tools import tool
from requests import get
import os

load_dotenv()
weather_cordinates_api_key =  os.getenv("WEATHER_CORDINATES_API_KEY")

#Tools

@tool("get_latitude_longitude", description="Get the latitude and longitude of a location")
def get_cordinates(city_name: str, country_code: str) -> str:
    """"Tool responsible to get the latitude and longitude of a location"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{country_code}&limit=5&appid={weather_cordinates_api_key}"
    response = get(url)
    if response.status_code in (200,201):
        data = response.json()
        if data:
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            return f"Latitude: {latitude}, Longitude: {longitude}"
        else:
            return "No data found"
    


@tool("find_weather", description="Find the weather using the user's input location")
def get_weather(location: str) -> str:
    """"Tool responsible to find the weather using the user's input location"""

if __name__ == "__main__":
    print("Hello from langchain-agents!")

    