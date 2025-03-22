# app/utils/langgraph_chatbot.py
import os
import json

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Dict, List, Any
from typing_extensions import TypedDict
from dotenv import load_dotenv

load_dotenv()

# 環境変数の設定
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def create_chatbot():
    """チャットボットグラフを作成して返す"""
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    llm = ChatAnthropic(api_key=ANTHROPIC_API_KEY, model="claude-3-haiku-20240307")
    
    graph_builder = StateGraph(State)
    
    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}
    
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    return graph_builder.compile()

# グローバルなグラフインスタンスを作成
chatbot_graph = create_chatbot()

# def process_message(user_input: str, session_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
#     """
#     ユーザー入力を処理し、応答を返す
    
#     Args:
#         user_input: ユーザーの入力メッセージ
#         session_history: これまでの会話履歴 (LangChainフォーマット)
        
#     Returns:
#         処理結果の辞書 {"messages": [...]}
#     """
#     # 履歴がない場合は新しいリストを作成
#     messages = session_history or []
    
#     # ユーザーメッセージを追加
#     messages.append({"role": "user", "content": user_input})
    
#     # グラフを実行
#     result = chatbot_graph.invoke({"messages": messages})
#     return result

def process_message(user_input: str, session_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    # 履歴がない場合は新しいリストを作成
    messages = session_history or []
    
    # ユーザーメッセージを追加
    messages.append({"role": "user", "content": user_input})
    
    # グラフを実行
    result = chatbot_graph.invoke({"messages": messages})
    
    # デバッグ情報を出力
    print("DEBUG: LangGraph result type:", type(result))
    print("DEBUG: Messages type:", type(result.get("messages", [])))
    if result.get("messages"):
        last_msg = result["messages"][-1]
        print("DEBUG: Last message type:", type(last_msg))
        print("DEBUG: Last message attributes:", dir(last_msg))
    
    return result

def convert_to_langchain_format(messages):
    """
    アプリケーション形式のメッセージをLangChain形式に変換
    
    Args:
        messages: アプリケーション形式のメッセージリスト
        
    Returns:
        LangChain形式のメッセージリスト
    """
    result = []
    for msg in messages:
        result.append({
            "role": msg.role,
            "content": msg.content
        })
    return result

# def extract_assistant_message(result):
#     """
#     LangGraphの結果から最新のアシスタントメッセージを抽出
    
#     Args:
#         result: LangGraphの結果辞書
        
#     Returns:
#         最新のアシスタントメッセージの内容
#     """
#     for msg in reversed(result["messages"]):
#         if msg.get("role") == "assistant":
#             return msg.get("content", "")
#     return ""

def extract_assistant_message(result):
    """
    LangGraphの結果から最新のアシスタントメッセージを抽出
    """
    if not result["messages"]:
        return ""
        
    last_message = result["messages"][-1]
    
    # AIMessageオブジェクトの場合
    if hasattr(last_message, "content"):
        return last_message.content
    
    # 万が一辞書の場合
    elif isinstance(last_message, dict):
        return last_message.get("content", "")
    
    return ""

# スタンドアロン実行用のコード
if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            result = process_message(user_input)
            print("Assistant:", extract_assistant_message(result))
        except Exception as e:
            print(f"Error: {e}")
            break

# import os
# import json

# from langchain_anthropic import ChatAnthropic
# # from langchain_community.document_loaders import WebBaseLoader
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.prebuilt import ToolNode, tools_condition

# from langgraph.types import Command, interrupt

# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.messages import ToolMessage, HumanMessage
# from langchain_core.tools import tool
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import PromptTemplate
# # from langchain_community.document_loaders import WebBaseLoader

# from typing import Annotated
# from typing_extensions import TypedDict
# from langsmith import Client
# from dotenv import load_dotenv

# load_dotenv()

# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGSMITH_API_KEY")
# os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT")
# os.environ["TAVIRY_API_KEY"] = os.environ.get("TAVIRY_API_KEY")

# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# llm = ChatAnthropic(api_key=ANTHROPIC_API_KEY, model="claude-3-haiku-20240307")

# client = Client()

# class State(TypedDict):
#     # Messages have the type "list". The `add_messages` function
#     # in the annotation defines how this state key should be updated
#     # (in this case, it appends messages to the list, rather than overwriting them)
#     messages: Annotated[list, add_messages]

# graph_builder = StateGraph(State)

# def chatbot(state: State):
#     return {"messages": [llm.invoke(state["messages"])]}


# # The first argument is the unique node name
# # The second argument is the function or object that will be called whenever
# # the node is used.
# graph_builder.add_node("chatbot", chatbot)
# graph_builder.set_entry_point("chatbot")
# graph_builder.set_finish_point("chatbot")
# graph = graph_builder.compile()

# def stream_graph_updates(user_input: str):
#     for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)


# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break

#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break

# def __init__():
#     stream_graph_updates()