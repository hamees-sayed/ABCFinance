import os
import serpapi
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader

def generate_news(query="finance india"):
    params = {
        "engine": "bing_news",
        "q": query,
        "cc": "in",
        "qft": 7,
        "api_key": os.environ.get("SERP_API_KEY")
    }

    search = serpapi.search(params)
    results = search.as_dict()
    return results["organic_results"]