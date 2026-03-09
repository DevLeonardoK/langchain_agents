from langgraph.graph import add_messages, StateGraph, END
from typing import Annotated
from typing_extensions import TypedDict, Annotated #Metadata#
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver #Memory RAM
from langchain_deepseek import ChatDeepSeek

#load envs
load_dotenv()


#state

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
#LLM
model = ChatDeepSeek(model='deepseek-chat', temperature=0)

#Chatbot node

def chatbot(state: State):
    response = model.invoke(state['messages'])
    return {'messages': [response]}

