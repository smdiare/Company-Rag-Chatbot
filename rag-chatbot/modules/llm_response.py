from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from utils.env_loader import get_env_var

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-8b", google_api_key=get_env_var("GOOGLE_API_KEY"))

def ask_llm(query, context):
    system = SystemMessage(content="You are a helpful assistant. Use the context to answer user questions.")
    human = HumanMessage(content=f"Context: {context}\n\nQuestion: {query}")
    return llm([system, human]).content