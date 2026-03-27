from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from config.config import settings
from src.utils.logger import logger, log_error_cleanly

# Initialize Embeddings (all-MiniLM-L6-v2 is perfect for Fargate CPUs)
logger.info("Loading HuggingFace Embeddings Model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

client = QdrantClient(
    url=settings.QDRANT_URL, 
    api_key=settings.HF_TOKEN # Use your secret key for cloud auth
)

def index_pdf(filepath, collection_name='research_papers'):
    logger.info(f"Starting indexing: {filepath}")
    
    try:
        docs = PyPDFLoader(file_path=filepath).load()
        
        split_docs = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        ).split_documents(documents=docs)
        
        
        for doc in split_docs:
            doc.metadata["source"] = filepath.split("/")[-1]

        QdrantVectorStore.from_documents(
            documents=split_docs,
            embedding=embeddings,
            url=settings.QDRANT_URL,
            api_key=settings.HF_TOKEN,
            collection_name=collection_name,
            force_recreate=False # Appends to the library instead of wiping it
        )
        logger.info(f"Successfully indexed {len(split_docs)} chunks to {collection_name}")
        
    except Exception as e:
        log_error_cleanly(e)

def query_research(question, collection_name="research_papers"):
    logger.info(f"Searching knowledge base for: '{question[:50]}'")
    
    try:
        # 1. Check if collection exists first to avoid crashes
        if not client.collection_exists(collection_name):
            return "The technical library is empty. Please upload and index your resume first."

        # 2. Use the client-based initialization (avoiding 'path')
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
        
        results = vector_store.similarity_search(query=question, k=3)
        
        if not results:
            return "I searched the library but found no relevant details in the documents."
        
        return "\n\n".join([doc.page_content for doc in results])
    
    except Exception as e:
        log_error_cleanly(e)
        return f"Technical library error: {str(e)}" # This will show you the REAL error in the UI

def clear_research_collection(collection_name="research_papers"):
    try:
        if client.collection_exists(collection_name=collection_name):
            client.delete_collection(collection_name=collection_name)
            logger.info(f"Cleared collection: {collection_name}")
            return f"Library {collection_name} cleared."
        return "Library already empty."
    except Exception as e:
        log_error_cleanly(e)
        return "Failed to clear knowledge base."