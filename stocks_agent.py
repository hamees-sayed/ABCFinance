import os
from serpapi import GoogleSearch
import google.generativeai as genai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(path="vec.db")
encoder = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")

def get_ticker(query: str):
    query_vector = encoder.encode(query).tolist()
    ndq = client.search(
                collection_name="ndq",
                query_vector=query_vector,
                limit=1
            )[0]
    nse = client.search(
                collection_name="nse",
                query_vector=query_vector,
                limit=1
            )[0]
    
    if ndq.score>nse.score:
        return ndq.payload["Symbol"]+":NASDAQ"
    else:
        return nse.payload["SYMBOL"]+":NSE"    

def get_stock_summary(ticker: str):
    params = {
        "engine": "google_finance",
        "q": ticker,
        "gl": "in",
        "api_key": "441a9056343a4481b099d44e177e65ea540d9a8b8af3f7b87c63da0235b74361"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results

def get_stock(query: str):
    """Get stock summary from full company name."""
    print("Agent called with query:", query)
    ticker = get_ticker(query)
    summary = get_stock_summary(ticker)
    # print("Returning summary:", summary)
    return summary

def get_news(query:str = "Tata Motors news"):
    '''Fetches the latest news of the company'''
    params = {
        "engine": "google_news",
        "q": query,
        "cc": "in",
        "qft": 7,
        "api_key": "441a9056343a4481b099d44e177e65ea540d9a8b8af3f7b87c63da0235b74361"
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results

genai.configure(api_key='AIzaSyDap6T0UIajYoMUXLjlcb7yf0_4EDD27Xs')
model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                            system_instruction='''You are a helpful financial assistant. Your name is Stock Bro.
                                                You were created by Advait and Hasan for the benefit of the user. Feel free to use emojis.
                                                You are an agent that provides useful information and summaries about stocks.
                                                Your goal is to help the user navigate the stock markets and give sound financial help.
                                                You have access to Stock Agent and News Agent. Include links from context in your answers.
                                                Prefer using relevent context from your history before calling a tool.
                                                Avoid asking the user follow up questions unless you really need to.    
                                                Answer all their queries promptly to the best of your ability, using the tools and context provided.
                                            ''',

                            tools=[get_stock, get_news]
                            )

chat = model.start_chat(enable_automatic_function_calling=True)

def stock_agent(query, history):
    if query=="":
        return "Don't make empty requests. Please ask me something about stocks!"
    if history==[]:
        chat.history = []
    
    response = chat.send_message(query)
    return response.text

if __name__ == '__main__':    
    input = "what is the stock price of Punjab National Bank?"
    response = chat.send_message(input)
    print(response.text+'\n')

    for content in chat.history:
        part = content.parts[0]
        print(content.role, "->", type(part).to_dict(part))
        print('-'*80)