import random
import gradio as gr
import google.generativeai as genai
from stocks_agent import get_stock

genai.configure(api_key='AIzaSyDap6T0UIajYoMUXLjlcb7yf0_4EDD27Xs')
model = genai.GenerativeModel( model_name='gemini-1.5-flash',
                               tools=[get_stock] )

chat = model.start_chat(enable_automatic_function_calling=True)

def random_response(message, history):
    print(history)
    return random.choice(["Yes", "No"])

def stock_agent(query, history):
    if history==[]:
        chat.history = []
    
    response = chat.send_message(query)
    return response.text

gr.ChatInterface(stock_agent).launch()