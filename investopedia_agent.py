import os
from dotenv import load_dotenv
import faiss
import json
from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.docstore.document import Document as LangchainDocument
import datasets

embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("faiss_index.bin")
with open("metadata.json", "r") as f:
    loaded_metadata = json.load(f)
ds = datasets.load_dataset("openvega-simon/investopedia", split="train")
RAW_KNOWLEDGE_BASE = [
    LangchainDocument(page_content=doc["md_content"], metadata={"title": doc["title"], "source": doc["url"]})
    for doc in ds
]
load_dotenv()

def get_context(query: str):
    query_embedding = embeddings_model.encode([query], normalize_embeddings=True).astype('float32')
    D, I = index.search(query_embedding, k=5)
    
    context_list = []
    sources = {}

    for j, i in enumerate(I[0]):
        page_content = RAW_KNOWLEDGE_BASE[i].page_content
        title = loaded_metadata[i]["title"]
        source = loaded_metadata[i]["source"]
        
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
    it engaging. If there are any equations wrap them in "$" for example "$x^2 + y^3 = 5$".
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