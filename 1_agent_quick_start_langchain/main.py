from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from langchain.tools import tool
from requests import get
import os
from pydantic import BaseModel, Field

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
            general_weather = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            return f"General Weather: {general_weather},\n Temperature: {temperature}°C,\n Humidity: {humidity}%,\n Wind Speed: {wind_speed} m/s"
         
#model = ChatDeepSeek(model="deepseek-reasoner", temperature=0.7, extra_body={"thinking": {"enabled": False,"type":"disabled"}})    --Use to disable thinking mode


#Structured output

class WeatherOutput(BaseModel):
    general_weather: str = Field(description="General weather description")
    temperature: str = Field(description="Temperature in Celsius")
    humidity: str = Field(description="Humidity porcentage")
    wind_speed: str = Field(description="Wind speed in m/s")

model = ChatDeepSeek(model="deepseek-chat", temperature=0.7)      
   
agent = create_agent(
    model=model,
    tools=[get_cordinates, get_weather],
    system_prompt="You are a helpful assistant that can find the weather of any location in the world",
    response_format=WeatherOutput
)
            
if __name__ == "__main__":
    print("Hello from langchain-agents!")
    user_input = input("Enter the city name and country code (e.g. London, UK): ")
    result =agent.invoke(
        {
            "messages":
            [
                {"role":"user",
                 "content":f"What is the weather in {user_input} ?"
                }
            ]
        }
    )
    #print(result['messages'][-1].content) --> No structured output, only text response
    print(result["structured_response"].model_dump_json(indent=4)) #--Structured output in JSON format
