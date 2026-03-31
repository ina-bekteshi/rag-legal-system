import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# RAG Imports
from langchain_community.embeddings import FakeEmbeddings
from langchain_groq import ChatGroq
from langchain_weaviate import WeaviateVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import weaviate

# Load environment variables
load_dotenv()

# -- RAG Setup --

# Persistent Weaviate client and RAG chain
client = None
rag_chain = None

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, rag_chain
    weaviate_host = os.getenv("WEAVIATE_HOST", "localhost")
    weaviate_port = int(os.getenv("WEAVIATE_PORT", "8080"))
    print(f"Connecting to Weaviate at {weaviate_host}:{weaviate_port}...")
    try:
        client = weaviate.connect_to_local(host=weaviate_host, port=weaviate_port)
        fake_embeddings = FakeEmbeddings(size=384)
        
        vector_store = WeaviateVectorStore(
            client=client,
            index_name="KushtetutaV3",
            text_key="text",
            embedding=fake_embeddings 
        )
        
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 5, "alpha": 0.3}
        )
        
        # Initialize LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0, 
        )
        
        prompt_template = """Ti je 'E-Juristi', një asistent inteligjent ligjor për Kushtetutën e Republikës së Shqipërisë.
        Përdor kontekstin e mëposhtëm për t'iu përgjigjur pyetjes së përdoruesit në gjuhën shqipe, në mënyrë profesionale dhe të qartë.
        Nëse nuk e di përgjigjen ose nuk gjendet në kontekstin e dhënë, thuaj thjesht që nuk ke informacione për këtë në bazën tënde të të dhënave, mos shpik informacione.

        Konteksti: {context}

        Pyetja: {query}

        Përgjigja: """
        
        custom_rag_prompt = PromptTemplate.from_template(prompt_template)
        
        rag_chain = (
            {"context": retriever | format_docs, "query": RunnablePassthrough()}
            | custom_rag_prompt
            | llm
            | StrOutputParser()
        )
        print("RAG System initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize RAG system: {e}")
        
    yield
    
    # Shutdown logic
    if client:
        client.close()
        print("Weaviate connection closed.")

app = FastAPI(title="E-Juristi API", lifespan=lifespan)

# Mount static files folder
app.mount("/static", StaticFiles(directory="static"), name="static")


# -- API Endpoints --

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not rag_chain:
        return ChatResponse(reply="Gabim: RAG sistemi nuk është i gatshëm. Ju lutem kontrolloni lidhjen me databazën (Weaviate).")
    
    try:
        response = rag_chain.invoke(req.message)
        return ChatResponse(reply=response)
    except Exception as e:
        print(f"Error during RAG generation: {e}")
        return ChatResponse(reply="Ndodhi një gabim gjatë procesimit të kërkesës tuaj. Ju lutem provoni përsëri.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chatbot_api:app", host="0.0.0.0", port=8000, reload=True)
