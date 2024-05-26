import os
import pandas as pd
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv
from pandasai import SmartDataframe
from pandasai.llm.google_gemini import GoogleGemini

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
llm = GoogleGemini(api_key=GOOGLE_API_KEY)

st.title('Data Analyst Agent')

csv_file = st.file_uploader('Upload a CSV file', type=['csv'])

if csv_file:
    df = pd.read_csv(csv_file)
    sdf = SmartDataframe(df, config={'llm': llm})
    st.write(df.head())
    prompt = st.text_area('Ask me questions about the data')
    if st.button('Generate'):
        if prompt:
            with st.spinner('Thinking...'):
                response = sdf.chat(prompt)
                if response != "/workspaces/ABCFinance/exports/charts/temp_chart.png":
                    st.success(response)

                st.set_option('deprecation.showPyplotGlobalUse', False)
                st.pyplot()
        else:
            st.warning('Please enter a prompt')