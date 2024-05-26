import random
import gradio as gr
import google.generativeai as genai
from stocks_agent import get_stock

genai.configure(api_key='AIzaSyDap6T0UIajYoMUXLjlcb7yf0_4EDD27Xs')
model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                              system_instruction='''You are a helpful financial assistant. Your name is Stock Bro.
                                                    You were created by Advait and Hasan for the benefit of the user. Feel free to use emojis.
                                                    You are an agent that provides useful information and summaries about stocks.
                                                    Your goal is to help the user navigate the stock markets and give sound financial help.
                                                    You have access to tools that provide stock information. Include links from context in your answers.
                                                    Prefer using relevent context from your history before calling a tool.
                                                    Avoid asking the user follow up questions unless you really need to.    
                                                    Answer all their queries promptly to the best of your ability, using the tools and context provided.
                                                ''',
                              tools=[get_stock]
                              )

chat = model.start_chat(enable_automatic_function_calling=True)

def stock_agent(query, history):    
    if history==[]:
        chat.history = []
    
    response = chat.send_message(query)
    return response.text

gr.ChatInterface(
    stock_agent, 
    title="Stock Bro",
    description="Your personal stock assistant!",
    textbox=gr.Textbox(placeholder="Ask me anything about stocks!", container=False, scale=7),
    examples=[
        "Is NVIDIA going up?", 
        "What is the stock price of Apple?", 
        "Give me a summary on Zomato. What is the public opinion of this stock?",
        "What is the latest information on Logitech?"
        ],
    cache_examples=False,
    retry_btn=None,
    undo_btn=None,
    theme=gr.themes.Default(),
    ).launch()