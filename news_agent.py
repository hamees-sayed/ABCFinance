import os
import requests
from dotenv import load_dotenv
from newsapi import NewsApiClient
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from datetime import datetime, timedelta, timezone
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
today = datetime.now()
yesterday = today - timedelta(days=1)
yesterday_date = yesterday.date().isoformat()
today_date = today.date().isoformat()

def generate_news(query="finance india"):
    url = "https://newsapi.org/v2/everything?"
    params = {
        "q": query,
        "language": "en",
        "from": yesterday_date,
        "to": today_date,
        "apiKey": os.environ.get("NEWS_API_KEY")
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    articles = response_json['articles']

    filtered_articles = []
    for article in articles:
        # Check if required fields are not null
        if article.get('content') and article.get('urlToImage') and article.get('title'):
            filtered_articles.append(article)

    return filtered_articles[:10]



def summarise_news(content: str):
    prompt_template = """
    You are a news reporter, in 150 words, summarize the following news article, focusing on the most important points:
    \n\n
    Article:\n {article}\n\n

    Context: Briefly explain the situation or background leading up to the news.
    Key Figures: Include any important people or organizations involved.
    Impact: Analyze the article's main idea and supporting arguments to provide insights into the topic. Identify any implications or consequences of the article's findings or arguments.
    Quotes: Incorporate relevant quotes from the article that support the main idea or add depth to the summary. Ensure quotes are accurately attributed to the correct individuals.
    Insights: Offer an analysis of what this news means in simpler terms.
    Omit unnecessary information and jargon. Strive for a clear, logical, concise, and objective summary that is easy to understand. Use emojis if required to keep it engaging.
    \n
    Summary:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["article"])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=os.environ.get("GOOGLE_API_KEY"))
    chain = LLMChain(llm=llm, prompt=prompt)
    context_data = {
        "article": content,
    }
    response = chain.invoke(context_data)
    return response['text']

def convert_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    human_readable_date = date_obj.strftime("%d %B, %Y")
    return human_readable_date

generate_news()