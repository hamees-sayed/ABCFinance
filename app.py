import pandas as pd
import streamlit as st
from investopedia_agent import generate_response
from data_analyst_agent import generate_data_analyst_response
from news_agent import generate_news, summarise_news, convert_date


def intro():
    import streamlit as st

    st.write("# Welcome to ABCFinance! 👋")
    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        Introducing ABCFinance, your all-in-one financial companion designed to streamline your financial
        insights and investment strategies. ABCFinance brings together powerful features to ensure you stay
        ahead in the world of finance:

        **👈 Select a tool from the dropdown on the left** to see some examples
        of what ABCFinance can do!

        ## Investopedia Agent
        Got questions about financial terms or concepts? Our Investopedia agent scrapes the vast resources of
        Investopedia to provide you with detailed answers and reliable references, enhancing your financial
        literacy and understanding.
        
        ## Stocks Agent
        Never miss a beat with real-time updates on your stocks. Our stocks agent uses Google Finance
        to deliver the latest stock prices, market movements, and portfolio performance, ensuring you're always in the know.

        ## Data Analysis Agent
        Upload your CSV files and let our data analysis agent work its magic.
        It provides comprehensive analysis, charts and insights into your data, helping you make data-driven
        decisions with ease and confidence.

        ## News Agent
        Stay informed with the latest financial news fetched directly from the internet summarised for you, keeping you updated
        on market trends, economic developments, and breaking news that matters to your investments.
    """
    )
    
def investopedia_agent():
    st.title('Investopedia Agent')

    prompt = st.text_area('Ask me questions about financial topics')
    if st.button('Ask'):
        if prompt:
            with st.spinner('Thinking...'):
                response, sources = generate_response(prompt)
                st.write(response)
                st.write("References:")
                for key, value in sources.items():
                    st.link_button(key, value)
        else:
            st.warning('Please enter a prompt')
            
def data_analysis_agent():
    st.title('Data Analysis Agent')

    csv_file = st.file_uploader('Upload a CSV file', type=['csv'])

    if csv_file:
        df = pd.read_csv(csv_file)
        st.write(df.head())
        prompt = st.text_area('Ask me questions about the data')
        if st.button('Generate'):
            if prompt:
                with st.spinner('Thinking...'):
                    response = generate_data_analyst_response(prompt, df)
                    if response != "/workspaces/ABCFinance/exports/charts/temp_chart.png":
                        st.success(response)
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    st.pyplot()
            else:
                st.warning('Please enter a prompt')
                
def news_agent():
    st.title('News Agent')

    prompt = st.text_area('Latest news on financial topics', value="Finance India")
    if st.button('Generate'):
        if prompt:
            with st.spinner('Thinking...'):
                response = generate_news(prompt)
                for result in response:
                    st.write(f"**{result['title']}**")
                    st.image(result['urlToImage'], 300)
                    st.write(summarise_news(result['content']))
                    st.markdown(f"[{result['source']['name']}]({result['url']}), {convert_date(result['publishedAt'])}")
                    st.markdown("---")
    
if __name__ == '__main__':
    page_names_to_funcs = {
        "—": intro,
        "Investopedia Agent 🧑‍🏫": investopedia_agent,
        "Stocks Agent 💹": "mapping_demo",
        "Data Analysis Agent 📊": data_analysis_agent,
        "News Agent 📰": news_agent,
    }

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()

