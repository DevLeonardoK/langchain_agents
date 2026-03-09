from langgraph.graph import add_messages, StateGraph, END
from typing import Annotated
from typing_extensions import TypedDict, Annotated #Metadata#
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver #Memory RAM
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
import os



#load envs
load_dotenv()


#state

class State(TypedDict):
    messages: Annotated[list, add_messages]


#system file reader tool
@tool("os_file_reader_tool", description="Tool for retrieving files from this directory")
def os_file_reader_tool():
    files = os.listdir("/home/devleonardo-ai/Documents/langchain_agents")
    return files

#LLM
model = ChatDeepSeek(model='deepseek-chat', temperature=0, tool=os_file_reader_tool)

#Chatbot node
def chatbot(state: State):
    response = model.invoke(state['messages'])
    return {'messages': [response]}



#builder = pipeline langgraph

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)
builder.set_entry_point("chatbot")
builder.add_edge("chatbot",END) #edge finalize the single node


#Construct the checkpointer database (memory)
checkpointer = InMemorySaver()

#Compile the pipeline with memory
graph = builder.compile(checkpointer=checkpointer)

#configurable to search and to insert session id to agent invoke
configurable = {
                    "configurable": 
                        {
                            "thread_id":"1"
                        }
                }

if __name__ == "__main__":
    user_input = input('Type to agent -> ')
    result = []
    while user_input.lower().strip() not in ['exit','sair']:
        result.append(graph.invoke(
            {
              "messages":
                [
                  {
                    "role":"user",
                    "content":user_input
                  }
                ]  
            }, config=configurable
        ))
        print(result[-1]['messages'][-1].content)
        user_input = input('Type to agent -> ')