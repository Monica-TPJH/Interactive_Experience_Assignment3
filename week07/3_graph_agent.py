from langchain_openai import ChatOpenAI
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import random

config = {"configurable": {"thread_id": "1"}}

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

# 配置LM Studio的ChatOpenAI
model = ChatOpenAI(
    base_url="http://localhost:1234/v1",  # LM Studio的API地址
    api_key="lm-studio",  # LM Studio不需要真实的API key
    model=available_model,  # 使用检测到的模型
    temperature=0.7,
)

weather = {}

@tool
def get_weather(query: str):
    """Call to check real-time weather in a single location."""
    # This is a placeholder, but don't tell the LLM that...
    
    if query in weather:
        return weather[query]
    
    random_temperature = f'{random.randint(10, 40)}°C'
    random_outlook = random.choice(["sunny", "cloudy", "rainy", "snowy"])

    data = {"city": query, "outlook": random_outlook, "temperature": random_temperature}
    weather[query] = data
    
    return data

tools = [get_weather]


# Define the graph
graph = create_react_agent(model, tools=tools)

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}, config=config):
        for value in event.values():
            for last_message in value["messages"]:
                if last_message.type == "ai":
                    if last_message.tool_calls:
                        print("  --- Tool call:", last_message.tool_calls)
                    else:
                        print("Assistant:", last_message.content)
                elif last_message.type == "tool":
                    print("  --- Tool response:", last_message.content)

while True:
    try:
        user_input = input("User: ")
        stream_graph_updates(user_input)
    # catch all exceptions
    except Exception as e:
        print(e)
        break