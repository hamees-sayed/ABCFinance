import pandas as pd
import asyncio
import base64
import json
import streamlit as st
from uagents.query import query
from uagents import Model
from investopedia_agent import generate_response
from data_analyst_agent import generate_data_analyst_response
from news_agent import generate_news, summarise_news, convert_date

def run_async(coro):
    """Helper function to run an asyncio coroutine in Streamlit."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()

investopedia_address="agent1qt45kuf6etamqgaklauz375g2l5fyymyg53kt0vkrlhjxlgsfdvhy2sju29"

class InvestopediaRequest(Model):
    query: str

class InvestopediaResponse(Model):
    answer: str

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

        Made by:    
        [Hamees Ul Hasan](https://github.com/hamees-sayed)  
        [Advait](https://github.com/rumourscape)
    """
    )
    st.info("We appreciate your engagement! Please note, this project at its current state does not support conversational memory, we are working on it. Thank you for your understanding.")
    

async def investopedia_agent():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me questions about Financial Topics 🧑‍🏫"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = await query(destination=investopedia_address, message=InvestopediaRequest(query=prompt), timeout=15.0)
        data = json.loads(response.decode_payload())
        decoded_response = data['answer']
        print(decoded_response)
        st.write(decoded_response)
        # with st.chat_message("assistant"):
        #     st.markdown(answer)
        #     st.markdown("References:")
        #     for key, value in sources.items():
        #         st.link_button(key, value)
        # st.session_state.messages.append({"role": "assistant", "content": decoded_response})
            

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

    prompt = st.text_area("Latest news on financial topics, e.g 'Stock Trends', 'Finance News'", value="Finance India")
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
    selected_demo = page_names_to_funcs[demo_name]
    if asyncio.iscoroutinefunction(selected_demo):
        run_async(selected_demo())
    else:
        selected_demo()


