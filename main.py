# imports
from dotenv import load_dotenv

# load in the .env variables
load_dotenv()

# imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# 2. Use a PDF Loader to extract text (It handles the 'open' and 'read' for you)
file_path = "ligj_8417_21101998_perditesuar-kushtetuta.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

# 3. Initialize Text Splitter
# Note: RecursiveCharacterTextSplitter is generally better than CharacterTextSplitter 
# as it tries to keep paragraphs and sentences together.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    add_start_index=True,
)

# 4. Split the documents
chunks = text_splitter.split_documents(docs)

# imports
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Get Embeddings Model
#embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Initialize ChromaDB as Vector Store
vector_store = Chroma(
    collection_name="test_collection",
    embedding_function=embeddings
)

# Save Document Chunks to Vector Store
ids = vector_store.add_documents(chunks)

# Query the Vector Store
results = vector_store.similarity_search(
    'Kushte të veçanta për të drejtat e njeriut',
    k=2
)

# Print Resulting Chunks
for res in results:
    print(f"* {res.page_content} [{res.metadata}]\n\n")