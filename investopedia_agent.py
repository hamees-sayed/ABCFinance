import os
import streamlit as st
import google.generativeai as genai
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import StuffDocumentsChain

client = QdrantClient(path="investopedia.db")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def get_context(query: str):
    query_vector = encoder.encode(query).tolist()

    results = client.search(
        collection_name="investopedia",
        query_vector=query_vector,
        limit=5
    )

    context_list = []
    sources = {}

    for result in results:
        page_content = result.payload["page_content"]
        title = result.payload["title"]
        source = result.payload["source"]
        
        context_list.append(page_content)
        sources[title] = source
    
    # Join context_list to create a single context string
    context = "\n".join(context_list)
    
    return context, sources

def generate_response(query: str):
    docs, sources = get_context(query)
    prompt_template = """
    As a friendly and informative financial assistant, your task is to provide a clear and comprehensive answer to the following question. 
    Use the provided context to derive your answer, ensuring all information comes directly from the context. Break down complex financial 
    concepts into easy-to-understand language, using analogies and relatable examples whenever possible. Focus on educating users and 
    empowering them to make informed financial decisions in a conversational style. Please provide detailed steps, 
    explanations, and examples where applicable to ensure the answer is thorough and informative.
    \n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key="AIzaSyArmteboc6fSdKz9tF_fbuCfKYhKy-8hMk")
    chain = LLMChain(llm=llm, prompt=prompt)
    context_data = {
        "context": docs,
        "question": query
    }
    response = chain.invoke(context_data)
    reference_links = ", ".join([f"[{key}]({value})" for key, value in sources.items()])
    
    answer = f"{response["text"]}\n\n{reference_links}"
    return answer

st.title('Investopedia Agent')

prompt = st.text_area('Ask me questions about the data')
if st.button('Generate'):
    if prompt:
        with st.spinner('Thinking...'):
            response = generate_response(prompt)
            if response != "/workspaces/ABCFinance/exports/charts/temp_chart.png":
                st.write(response)
    else:
        st.warning('Please enter a prompt')