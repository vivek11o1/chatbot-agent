#import dependencies
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from typing import TypedDict , Annotated, List
import os
from dotenv import load_dotenv 
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
import sqlite3

#load .env file dependencies and load llm
load_dotenv()

#API_call
API_key = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model = "openai/gpt-OSS-120B"
)

#database connection
conn = sqlite3.connect(database = 'chatbot.db', check_same_thread = False)


#define state of the graph
class chatState(TypedDict):
    messages : Annotated[List[BaseMessage], add_messages]
    
#define corrosponding nodeFunction
def chatFunction(state : chatState):
    #extract message from input state
    messages = state['messages']
    
    #invoke llm with extracted messages
    response = model.invoke(messages)
    
    #return response
    return {'messages':[response]}

#define graph
graph = StateGraph(chatState)

#define nodes and edges
graph.add_node('chatFunction', chatFunction)

graph.add_edge(START,'chatFunction')
graph.add_edge('chatFunction',END)

#set checkpointer
checkpointer = SqliteSaver(conn = conn)

#compile the graph
ChatBot = graph.compile(checkpointer = checkpointer)


#returning all thread_id list from the database
def get_all_thread_id():
    all_thread_id = set()
    for checkpoint in checkpointer.list(None):
        all_thread_id.add(checkpoint.config['configurable']['thread_id'])
        
    return list(all_thread_id)









#execute
# while True:
#     config = {"configurable":{"thread_id":"1"}}
#     User_input = input("Type here: ")
#     print("Human_text: ", User_input)
#     if User_input in ["quit","bye","exit"]:
#         break
    
#     for message_chunk, metadata in ChatBot.stream(
#     {'messages':[HumanMessage(content = User_input)]},
#     config = {"configurable":{"thread_id":"thread_id 1"}},
#     stream_mode = 'messages'):
        
#         if message_chunk:
#             print(message_chunk.content, end=" ", flush = True )
            
     
     
     
     
     
     
     
     
     
            
    # response = ChatBot.invoke({'messages':[HumanMessage(content = User_input)]}, config = config)
    # print("AI_text: ", response['messages'][-1])

# for message_chunk, metadata in ChatBot.stream(
#     {'messages':[HumanMessage(content = "what is the recipe to make pasta")]},
#     config = {"configurable":{"thread_id":"1"}},
#     stream_mode = 'messages'
# ):
#     if message_chunk:
#         print(message_chunk.content, end=" ", flush = True )
