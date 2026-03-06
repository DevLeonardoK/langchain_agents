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
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph

AUTH = (USERNAME, PASSWORD)


@tool("verify_neo4j_connection", description="Tool to verify connection to neo4j database")
def verify_neo4j_connection():
    """Tool responsible to verify the connection to neo4j database, this tool will be used in the agent's workflow to check if the connection to the database is successful or not"""
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        try:
            driver.verify_connectivity()
            return "Connected to Neo4j successfully!"
        except Exception as e:
            return f"Connection failed: {str(e)}"

@tool("query_neo4j_database", description="Tool to query neo4j database")

def get_neo4j_database_schema() -> str:
    """"Tool responsible to query the neo4j database and return the schema of the database, this tool will be used in the agent's workflow to get the schema of the database and use it to generate cypher queries based on user questions"""
    with Neo4jGraph(url=URI, username=USERNAME, password=PASSWORD, database=DATABASE, enhanced_schema=True).schema as graph:
        try:
            return str(graph)
        except Exception as e:
            return f"Failed to get database schema: {str(e)}"
