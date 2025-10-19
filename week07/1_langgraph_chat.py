from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
import requests

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

memory = MemorySaver()

# The `config` dictionary is used to pass configuration to the graph
# In this case, we are setting the `thread_id` to store the state of the conversation
config = {"configurable": {"thread_id": "1"}}

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def check_lm_studio_models():
    """检查LM Studio中可用的模型"""
    try:
        response = requests.get("http://localhost:1234/v1/models")
        if response.status_code == 200:
            models = response.json()
            if models.get('data'):
                print("🎯 LM Studio中可用的模型:")
                for i, model in enumerate(models['data']):
                    print(f"   {i+1}. {model['id']}")
                return models['data'][0]['id']  # 返回第一个可用模型
            else:
                print("❌ LM Studio中没有加载任何模型")
                return None
        else:
            print(f"❌ 无法连接到LM Studio (状态码: {response.status_code})")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到LM Studio。请确保:")
        print("   1. LM Studio正在运行")
        print("   2. 本地服务器已启动 (通常在端口1234)")
        print("   3. 已加载至少一个模型")
        return None
    except Exception as e:
        print(f"❌ 检查模型时出错: {e}")
        return None

# 检查并获取可用模型
print("🔍 正在检查LM Studio...")
available_model = check_lm_studio_models()

if not available_model:
    print("\n💡 解决步骤:")
    print("   1. 打开LM Studio应用")
    print("   2. 在'模型'页面下载并加载一个模型")
    print("   3. 启动本地服务器 (在'开发者'页面)")
    print("   4. 重新运行此脚本")
    exit(1)

print(f"✅ 使用模型: {available_model}")

graph_builder = StateGraph(State)

# 配置LM Studio的ChatOpenAI
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",  # LM Studio的API地址
    api_key="lm-studio",  # LM Studio不需要真实的API key，但需要提供一个
    model=available_model,  # 使用检测到的模型
    temperature=0.7,
)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}, config=config):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        stream_graph_updates(user_input)
    # catch all exceptions
    except Exception as e:
        print(e)
        break