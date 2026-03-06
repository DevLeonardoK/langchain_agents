#Agent database with memory - no vectorization#

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from pydantic import BaseModel,Field
import os

#environment variables
load_dotenv()

URI = os.getenv("URI_DATABASE_NEO4J")
USERNAME = os.getenv("USERNAME_NEO4J")
PASSWORD = os.getenv("PASSWORD_NEO4J")
DATABASE = os.getenv("DATABASE_NEO4J")

