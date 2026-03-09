from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_deepseek import ChatDeepSeek
from typing import Annotated
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

#TypedDict é um dicionário onde passa um tipo, e um dado
class State(TypedDict):
    messages: Annotated[list, add_messages]
    #Tipo lista, e adição de mensagens, lista de mensagens

model = ChatDeepSeek(model='deepseek-chat', temperature=0.6)

def chatbot(state: State):
    response = model.invoke(state['messages'])
    return {"messages": [response]}

#Checkpointer = Estado atual daquele ponto
checkpointer = InMemorySaver()


#StateGraph = Responsável por construir o workflow/pipeline do agent

builder = StateGraph(State)
builder.add_node("chatbot",chatbot)
builder.set_entry_point("chatbot")
builder.add_edge("chatbot", END)

#builder.compile = Fluxo do agente e salvando na memória
graph = builder.compile(checkpointer=checkpointer)

#Configuração para usar memória - Utiliza thread_id como identificador
config = {"configurable":{"thread_id": "1"}}

#Chamar agent, simulando uma conversa. ATENÇÃO NO JSON E NOS ATRIBUTOS DO 'STATE'
result = [] 
result.append(graph.invoke(
    {
        "messages":
        [
            {
             "role":"user", 
             "content": "Olá, meu nome é Leonardo Kremer"
            }
        ]
    }, config=config
)
)
#Agent salvo na memória

result.append(graph.invoke(
    {
        "messages":
        [
            {
             "role": "user",
             "content": "Qual é o meu nome ?" 
            }
        ]
    }, config=config
))

print(result[-1]['messages'][-1].content)