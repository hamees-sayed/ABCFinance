import serpapi
import pydantic
from uagents import Agent, Context, Model, Bureau

class NewsSummary(Model):
    query: str = pydantic.Field(description="The query for the news summary", example="finance")

reporter = Agent(name="reporter", seed="news agent")

def generate_news(query: str):
    params = {
        "engine": "google_news",
        "q": query,
        "gl": "in",
        "api_key": "441a9056343a4481b099d44e177e65ea540d9a8b8af3f7b87c63da0235b74361"
    }

    search = serpapi.search(params)
    results = search.as_dict()
    return results['news_results'][:5]

@reporter.on_message(model=NewsSummary)
async def news_summary(ctx: Context, sender: str, search: NewsSummary):
    search_query = search.query
    # ctx.logger.info(generate_news(search_query))
    return generate_news(search_query)
    
bureau = Bureau()
bureau.add(reporter)