from langgraph.graph import add_messages, StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Annotated
from typing_extensions import TypedDict, Annotated #Metadata#
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver #Memory RAM
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
import os
from pathlib import Path



#load envs
load_dotenv()


#state

class State(TypedDict):
    messages: Annotated[list, add_messages]


#system file reader tool

@tool("os_file_reader_tool", description="Tool for retrieving files from specified directory")
def os_file_reader_tool(path:str = "."):
    """Tool to list files in a specified directory"""
    
    path_wrapper = Path(path).iterdir()
    
    return [
            f"Identification: {r.name}, is_file: {r.is_file()}, is_dir: {r.is_dir()}"
            for r in path_wrapper
        ]
#LLM
model = ChatDeepSeek(model='deepseek-chat', temperature=0).bind_tools([os_file_reader_tool]) #Tool knowledge for the LLM, but it does not run tools

#tool node
tools =[os_file_reader_tool]
tool_node = ToolNode(tools) #tool execution (run)

#Chatbot node
def chatbot(state: State):
    response = model.invoke(state['messages'])
    return {'messages': [response]}


#function to decide tool execution
def should_tool_call(state: State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return "tools"
    return END
    
    
#builder = pipeline langgraph

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)
builder.add_node("tools", tool_node)

builder.set_entry_point("chatbot")
builder.add_conditional_edges("chatbot", should_tool_call) #origin node to destination
builder.add_edge("tools","chatbot") #fixed pipeline


#Construct the checkpointer database (memory)
checkpointer = InMemorySaver()

#Compile the pipeline with memory
graph = builder.compile(checkpointer=checkpointer)

#configurable dict to set the session thread_id for the agent
configurable = {
                    "configurable": 
                        {
                            "thread_id":"2"
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