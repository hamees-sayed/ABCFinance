import os
import requests
from dotenv import load_dotenv
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from uagents import Agent, Model, Context
from uagents.setup import fund_agent_if_low
import asyncio

load_dotenv()
today = datetime.now()
yesterday = today - timedelta(days=1)
yesterday_date = yesterday.date().isoformat()
today_date = today.date().isoformat()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class NewsRequest(Model):
    query: str

class NewsResponse(Model):
    answer: str

def generate_news(query="stock trends in india"):
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
        if article.get('content') and article.get('urlToImage') and article.get('title'):
            filtered_articles.append(article)

    return filtered_articles[:10]

def summarise_news(content: str):
    prompt_template = """
    You are a news reporter, in 150 words, summarize the following news article, focusing on the most important points and use emojis if required to keep it engaging.:
    \n\n
    Article:\n {article}\n\n

    Context: Briefly explain the situation or background leading up to the news.
    Key Figures: Include any important people or organizations involved.
    Impact: Analyze the article's main idea and supporting arguments to provide insights into the topic. Identify any implications or consequences of the article's findings or arguments.
    Quotes: Incorporate relevant quotes from the article that support the main idea or add depth to the summary. Ensure quotes are accurately attributed to the correct individuals.
    Insights: Offer an analysis of what this news means in simpler terms.
    Omit unnecessary information and jargon. Strive for a clear, logical, concise, and objective summary that is easy to understand.
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

NewsAgent = Agent(
    name="NewsAgent",
    seed="News Agent",
    port=8000,
    endpoint=["https://abcfinance.onrender.com/submit"]
)

fund_agent_if_low(NewsAgent.wallet.address())

@NewsAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f"News Agent Address: {ctx.address}")

@NewsAgent.on_query(model=NewsRequest, replies={NewsResponse})
async def query_handler(ctx: Context, sender: str, msg: NewsRequest):
    try:
        answer = generate_news(msg.query)
        await ctx.send(sender, NewsResponse(answer=str(answer)))
    except Exception as e:
        err_msg = f"Error: {e}"
        ctx.logger.info(err_msg)

if __name__ == "__main__":
    NewsAgent.run()
