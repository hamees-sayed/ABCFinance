import os
import serpapi
from datetime import datetime, timedelta
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def generate_news(query="finance india"):
    params = {
        "q": query,
        "category": "finance",
        "language":'en',
        "country":'us',
        "from_param":
        "api_key": os.environ.get("NEWS_API_KEY")
    }

    search = serpapi.search(params)
    results = search.as_dict()
    return results["organic_results"]