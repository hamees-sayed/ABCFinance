import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

client = QdrantClient(path="investopedia.db")
encoder = SentenceTransformer("all-MiniLM-L6-v2")
load_dotenv()

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
    
    context = "\n".join(context_list)
    
    return context, sources

def generate_response(query: str):
    docs, sources = get_context(query)
    prompt_template = """
    You are a friendly and informative financial assistant, your task is to provide a clear and comprehensive answer to the following question.
    Use the provided context to derive your answer, ensuring all information comes directly from the context. Break down complex financial 
    concepts into easy-to-understand language, using analogies and relatable examples whenever possible. Focus on educating users and 
    empowering them to make informed financial decisions in a conversational style. Please provide detailed steps, 
    explanations, and examples where applicable to ensure the answer is thorough and informative. Use emojis if required to keep
    it engaging.
    \n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=os.environ.get("GOOGLE_API_KEY"))
    chain = LLMChain(llm=llm, prompt=prompt)
    context_data = {
        "context": docs,
        "question": query
    }
    response = chain.invoke(context_data)
    
    answer = f"{response['text']}\n\n"
    return answer, sources