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
import platform



#load envs
load_dotenv()


#state

class State(TypedDict):
    messages: Annotated[list, add_messages]


#system file reader tool
@tool("os_file_reader_tool", description="Tool for retrieving files from specified directory")
def os_file_reader_tool(path:str = "."):
    """Tool to list files in a specified directory"""
    
    path_wrapper = Path(path)
    if path_wrapper.exists() != False:

        return [
                f"Identification: {r.name}, is_file: {r.is_file()}, is_dir: {r.is_dir()}"
                for r in path_wrapper.iterdir()
            ]
    else:
        return "This directory is not valid, check the path" 

#get system os
@tool("get_system_os_specs", description="Tool to get the system OS information: system (Linux/Windows/macOS), version, and architecture")
def get_system_os_specs():
    """
    Returns detailed system OS information.

    This tool helps an agent determine the appropriate nomenclature
    for commands, paths, or navigation based on the host OS.

    Returns:
        dict: {
            "system": "Windows/Linux/macOS",
            "version": "OS version string",
            "architecture": "x86_64, ARM, etc."
        }
    """
    p = platform
    response = {
                "system": p.system(),
                "version": p.version(),
                "architecture": p.machine()
                }
    return response
    
#save file
@tool("save_file_tool", description="Tool to save a file with specified name and extension")
def save_file_tool(file_name: str, extension:str, content:str, path:str = "."):
    """
    Saves content to a file.
    
    Args:
        filename: Name of the file (without extension)
        extension: File extension (e.g. .txt, .py, .json)
        content: Content to write to the file
        path: Directory path where the file will be saved
    """
    
    p = Path(path)
    if p.parent.exists():
        full_path = f"{p}/{file_name}{extension}"
        path_file = Path(full_path)
        path_file.write_text(content)
        return {"tool_output":"File created"}
    else:
        return {"tool_output":"The path: {p.parent} does not exist, check !"}        
        



#LLM
model = ChatDeepSeek(model='deepseek-chat', temperature=0).bind_tools([os_file_reader_tool,get_system_os_specs,save_file_tool]) #Tool knowledge for the LLM, but it does not run tools

#tool node
tools =[os_file_reader_tool, get_system_os_specs,save_file_tool]
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
                            "thread_id":"3"
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