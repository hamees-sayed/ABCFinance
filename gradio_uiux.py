import random
import gradio as gr
import google.generativeai as genai
from investopedia_agent import get_context

genai.configure(api_key='AIzaSyArmteboc6fSdKz9tF_fbuCfKYhKy-8hMk')

model = genai.GenerativeModel(model_name='gemini-1.5-flash', 
            system_instruction="""
                You are Finance Bro a friendly and informative financial assistant, your task is to provide a clear and comprehensive answer to the following question. 
                Use the provided context to derive your answer, ensuring all information comes directly from the context. Break down complex financial 
                concepts into easy-to-understand language, using analogies and relatable examples whenever possible. Focus on educating users and 
                empowering them to make informed financial decisions in a conversational style. Please provide detailed steps, 
                explanations, and examples where applicable to ensure the answer is thorough and informative.""",
            tools=[get_context])

chat = model.start_chat(enable_automatic_function_calling=True)

def invest_agent(query, history):    
    if history==[]:
        chat.history = []
    
    response = chat.send_message(query)
    return response.text
    
gr.ChatInterface(
    invest_agent, 
    title="Finance Bro",
    description="Your personal finance assistant!",
    textbox=gr.Textbox(placeholder="Ask me anything about finance!", container=False, scale=7),
    examples=[
        "What are some good options for retirement savings if I'm just starting out", 
        "How to save for a house?", 
        "Can you explain what a stock is and how buying shares can benefit me in the long term?",
        "What factors affect my credit score, and how can I improve it?"
        "Recommend me some good future trading platforms."
        ],
    cache_examples=False,
    retry_btn=None,
    undo_btn=None,
    theme=gr.themes.Default(),
).launch()

