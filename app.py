import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import FakeEmbeddings

# 1. Load and Split (Same as before)
loader = PyPDFLoader("ligj_8417_21101998_perditesuar-kushtetuta.pdf")
chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(loader.load())

fake_embeddings = FakeEmbeddings(size=384)

# 2. Connect to Weaviate
client = weaviate.connect_to_local()

try:
    # 3. Initialize Vector Store WITHOUT a local embedding model
    # Weaviate will use the 'text2vec-transformers' module defined in Docker
    vector_store = WeaviateVectorStore(
        client=client,
        index_name="AlbanianConstitution",
        text_key="text",
        # We pass None here because the SERVER handles the embedding
        embedding=fake_embeddings 
    )

    # 4. Add Documents (Raw text is sent; Weaviate embeds it internally)
    vector_store.add_documents(chunks)

    # 5. Search
    # Weaviate will automatically turn this string into a vector using the same model
    results = vector_store.similarity_search("Te drejtat e njeriut")
    
    for res in results:
        print(f"Gjetur: {res.page_content[:200]}...")

finally:
    client.close()