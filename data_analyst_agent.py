import os
import io
import asyncio
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm.google_gemini import GoogleGemini
from uagents import Agent, Model, Context
from uagents.setup import fund_agent_if_low
import asyncio

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
llm = GoogleGemini(api_key=GOOGLE_API_KEY)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class DataRequest(Model):
    query: str
    df: str

class DataResponse(Model):
    answer: str

def generate_data_analyst_response(prompt: str, df: str):
    df_pd = pd.read_csv(io.StringIO(df))
    print(df_pd.head())
    sdf = SmartDataframe(df_pd, config={'llm': llm})
    response = sdf.chat(prompt)
    return response

DataAgent = Agent(
    name="DataAgent",
    port=8001,
    seed="Data Agent",
    endpoint=["http://127.0.0.1:8001/submit"]
)

fund_agent_if_low(DataAgent.wallet.address())

@DataAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f"Data Agent Address: {ctx.address}")

@DataAgent.on_query(model=DataRequest, replies={DataResponse})
async def query_handler(ctx: Context, sender: str, msg: DataRequest):
    try:
        answer = generate_data_analyst_response(msg.query, msg.df)
        await ctx.send(sender, DataResponse(answer=str(answer)))
    except Exception as e:
        err_msg = f"Error: {e}"
        ctx.logger.info(err_msg)

if __name__ == "__main__":
    DataAgent.run()