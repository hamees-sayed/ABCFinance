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
    """Get stock summary from stock name."""
    print("Agent called with query:", query)
    ticker = get_ticker(query)
    summary = get_stock_summary(ticker)
    print("Returning summary:", summary)
    return summary

if __name__ == '__main__':
    # GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key='AIzaSyDap6T0UIajYoMUXLjlcb7yf0_4EDD27Xs')
    model = genai.GenerativeModel( model_name='gemini-1.5-flash',
                                tools=[get_stock] )
    
    input = "what is the stock price of Punjab National Bank?"

    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(input)
    print(response.text+'\n')
    for content in chat.history:
        part = content.parts[0]
        print(content.role, "->", type(part).to_dict(part))
        print('-'*80)