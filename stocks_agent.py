import os
import serpapi
import google.generativeai as genai
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import dotenv

dotenv.load_dotenv()

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2", normalize_embeddings=True)

print(os.environ.get("SERP_API_KEY"))

client = chromadb.PersistentClient(path="agents.db")

nse_client = client.get_collection("nse", embedding_function=sentence_transformer_ef)
ndq_client = client.get_collection("ndq", embedding_function=sentence_transformer_ef)

def get_ticker(query: str):
    ndq = ndq_client.query(query_texts=query, n_results=1)
    nse = nse_client.query(query_texts=query, n_results=1)
    print(ndq.get("metadatas")[0][0]["Symbol"])

    if ndq.get('distances')[0]>nse.get('distances')[0]:
        return ndq.get("metadatas")[0][0]["Symbol"]+":NASDAQ"
    else:
        return nse.get("metadatas")[0][0]["SYMBOL"]+":NSE"    

def get_stock_summary(ticker: str):
    params = {
        "engine": "google_finance",
        "q": ticker,
        "gl": "in",
        "api_key": os.environ.get("SERP_API_KEY")
    }

    search = serpapi.search(params)
    results = search.as_dict()
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
        "api_key": os.environ.get("SERP_API_KEY")
    }

    search = serpapi.search(params)
    results = search.as_dict()
    return results

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
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