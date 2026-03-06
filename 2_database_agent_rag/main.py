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

#Neo4j Database connection details
from neo4j import GraphDatabase

AUTH = (USERNAME, PASSWORD)


@tool("verify_neo4j_connection", description="Tool to verify connection to neo4j database")
def verify_neo4j_connection():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        try:
            driver.verify_connectivity()
            return "Connected to Neo4j successfully!"
        except Exception as e:
            return f"Connection failed: {str(e)}"


