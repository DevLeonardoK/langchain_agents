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
    """"Tool responsible to get the latitude and longitude of a location, the first step to find the weather is to get the cordinates of the location, this tool will be used in the agent's workflow"""
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
    


@tool("find_weather", description="Find the weather using the user's input location (latitude and longitude)")
def get_weather(latitude: str, longitude: str) -> str:
    """"Tool responsible to find the weather using the user's input location (latitude and longitude). This tool will be used to return the temperature, humidity, general weather and wind speed of the location, """
    link = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_cordinates_api_key}&lang=en&units=metric"
    response = get(link)
    if response.status_code in (200,201):
        data = response.json()
        if data:
            general_weather = data['weather'][0].description
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            return f"General Weather: {general_weather},\n Temperature: {temperature}°C,\n Humidity: {humidity}%,\n Wind Speed: {wind_speed} m/s"
            
            
if __name__ == "__main__":
    print("Hello from langchain-agents!")

    