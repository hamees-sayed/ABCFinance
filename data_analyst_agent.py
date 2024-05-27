import os
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm.google_gemini import GoogleGemini

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
llm = GoogleGemini(api_key=GOOGLE_API_KEY)

def read_df(csv_file: str):
    df = pd.read_csv(csv_file)
    return df

def generate_data_analyst_response(prompt: str, df):
    sdf = SmartDataframe(df, config={'llm': llm})
    response = sdf.chat(prompt)
    return response