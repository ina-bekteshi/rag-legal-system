import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import FakeEmbeddings
from langchain_groq import ChatGroq, data  # New Groq Import
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings # Local Free Embeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
import weaviate

# Load environment variables (Make sure GROQ_API_KEY is in your .env)
load_dotenv()

# 1. Get Embeddings Model (Local & Free)
# Using a multilingual model since your query is in Albanian
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# )

# # 2. Initialize ChromaDB as Vector Store
# # Ensure 'persist_directory' matches where you saved your chunks earlier
# vector_store = Chroma(
#     collection_name="test_collection",
#     embedding_function=embeddings,
#     persist_directory="./chroma_db" 
# )

# 3. Set Chroma Vector Store as the Retriever
# retriever = vector_store.as_retriever(search_kwargs={"k": 5})


# 1. Load and Split (Same as before)
loader = PyPDFLoader("ligj_8417_21101998_perditesuar-kushtetuta.pdf")
chunks = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=150, separators=["NENI", "\n\n", "\n", " "]).split_documents(loader.load())

fake_embeddings = FakeEmbeddings(size=384)

# 2. Connect to Weaviate
client = weaviate.connect_to_local()

# collection = client.collections.get("AlbanianConstitution")
# total = collection.aggregate.over_all(total_count=True)
# print(f"Numri total i chunks në DB: {total.total_count}")

print(f"Numri total i faqeve të lexuara: {len(chunks)}")

# 1. Kontrollojmë sa chunks përmbajnë tekstin "Neni 20"
target_text = "Neni 20"
# Krijojmë një listë me indekset e chunks ku gjendet teksti
found_indices = [i for i, c in enumerate(chunks) if target_text.lower() in c.page_content.lower()]

print(f"\n--- REZULTATET E TESTIT ---")
print(f"Numri total i chunks: {len(chunks)}")
print(f"U gjetën {len(found_indices)} chunks që përmbajnë '{target_text}'")

# 2. Shfaq përmbajtjen duke përdorur indeksin e saktë
if found_indices:
    for idx in found_indices[:3]: # Shohim 3 të parët për siguri
        print(f"\n--- Chunk #{idx} (Faqja: {chunks[idx].metadata.get('page', 'N/A')}) ---")
        print(chunks[idx].page_content)
        print("-" * 40)
else:
    print(f"ALARM: '{target_text}' nuk u gjet në asnjë chunk! Kontrollo PDF-në ose Splitter-in.")

try:
    # 3. Initialize Vector Store WITHOUT a local embedding model
    # Weaviate will use the 'text2vec-transformers' module defined in Docker
    vector_store = WeaviateVectorStore(
        client=client,
        index_name="KushtetutaV3",
        text_key="text",
        # We pass None here because the SERVER handles the embedding
        embedding=fake_embeddings 
    )

    vector_store.add_documents(chunks)

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 5,
            #"search_type": "hybrid", # Aktivizon kërkimin hibrid
            "alpha": 0.3
        }
    )

    docs = retriever.invoke("Neni 20")
    print("--- COPAT E GJETURA NGA DATABASE ---")
    for d in docs:
        print(d.page_content[:200]) # Shiko nëse fjala "Neni 20" shfaqet këtu
    print("----------------------------------")

    # 4. Initialize the Groq LLM instance
    # 'llama-3.3-70b-versatile' is excellent for complex legal reasoning
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0, # Set to 0 for factual legal answers
    )

    # 5. Create Document Parsing Function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # 6. Create the Prompt Template
    prompt_template = """Përdorni kontekstin e mëposhtëm për t'iu përgjigjur pyetjes së përdoruesit. 
    Nëse nuk e dini përgjigjen bazuar në kontekst, thoni që nuk e dini dhe kërkoni ndjesë.

    Konteksti: {context}

    Pyetja: {query}

    Përgjigja: """

    custom_rag_prompt = PromptTemplate.from_template(prompt_template)

    # 7. Create the RAG Chain
    rag_chain = (
        {"context": retriever | format_docs, "query": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )

    # 8. Query the RAG Chain
    response = rag_chain.invoke("Cfare thot Neni 19 i kushtetutes se Republikes se Shqiperise ne fjale te thjeshta?")
    print(response)

finally:
    client.close()