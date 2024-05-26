import asyncio
import serpapi
import pydantic
import streamlit as st
from uagents import Agent, Context, Model, Bureau

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class NewsSummary(Model):
    query: str = pydantic.Field(description="The query for the news summary", example="finance")

class NewsResult(Model):
    result: list

reporter = Agent(name="reporter", seed="news agent")

def generate_news(query="finance india"):
    params = {
        "engine": "duckduckgo",
        "q": query,
        "cc": "in",
        "qft": 7,
        "api_key": "441a9056343a4481b099d44e177e65ea540d9a8b8af3f7b87c63da0235b74361"
    }

    search = serpapi.search(params)
    results = search.as_dict()
    return results["news_results"]

@reporter.on_message(model=NewsSummary, replies=NewsResult)
async def news_summary(ctx: Context, sender: str, search: NewsSummary):
    search_query = search.query
    response = generate_news(search_query)
    print(response)
    for result in response:
        if "..." not in result["snippet"] and result.get("thumbnail"):
            st.write(f"**{result["title"]}**")
            st.write(result["snippet"])
            st.image(result["thumbnail"])
            st.markdown(f"[{result["source"]}]({result["link"]}), {result["date"]}")
            st.markdown("---")
    
bureau = Bureau()
bureau.add(reporter)