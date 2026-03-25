from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from config.config import settings
from src.utils.logger import logger, log_error_cleanly

# Initialize Embeddings
logger.info("Loading HuggingFace Embeddings Model (all-MiniLM-L6-v2)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                   model_kwargs={'device': 'cpu'})

client = QdrantClient(url="http://127.0.0.1:6333")

def index_pdf(filepath, collection_name='research_papers'):
    """Loads, splits, and embeds a PDF into the Qdrant vector store.

    Args:
        filepath (str): The path of the file
        collection_name (str, optional): The name of the collection. Defaults to 'research_papers'.
    """
    logger.info(f"Starting indexing for file: {filepath}")
    
    try:
        docs = PyPDFLoader(file_path=filepath).load()
        logger.info(f"PDF loaded: {len(docs)} pages found.")
        
        split_docs = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                    chunk_overlap=100
                                                    ).split_documents(documents=docs)
        logger.info(f"Document split into {len(split_docs)} chunks.")
        
        # Create Vector Store
        logger.info(f"Generating embeddings and saving to collection: {collection_name}...")
        QdrantVectorStore.from_documents(
                client=client,
                embedding=embeddings, 
                documents=split_docs,
                path="./data/qdrant_db",
                collection_name=collection_name,
            )
        logger.info("Indexing complete. Knowledge base updated.")
        
    except Exception as e:
        log_error_cleanly(e)
    

def query_research(question, collection_name="research_papers"):
    """Performs a similarity search in the vector store.

    Args:
        question (str): The query asked by the user.
        collection_name (str, optional): The name of the collection. Defaults to "research_papers".

    Returns:
        context: Retrieves top 3 relevant documents.
    """
    logger.info(f"Searching research for: '{question[:50]}...'")
    
    try:
        vector_store = QdrantVectorStore.from_existing_collection(
            client=client,
            embedding=embeddings,
            path='./data/qdrant_db',
            collection_name=collection_name
        )
        
        # Returning top 3 results
        results = vector_store.similarity_search(query=question, k=3)
        
        if not results:
            logger.warning("No relevant documents found in vector store.")
            return "No relevant info found."
        
        logger.info(f"Found {len(results)} relevant chunks.")
        
        # Combine results into one string for AVA's context
        context = "\n\n".join([doc.page_content for doc in results])
        
        return context
    
    except Exception as e:
        log_error_cleanly(e)
        return "Error querying research database."

def clear_research_collection(collection_name="research_papers"):
    """Wipes out entire collection data

    Args:
        collection_name (str, optional): name of the collection. Defaults to "research_papers".
    """
    try:
        if client.collection_exists(collection_name=collection_name):
            client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully.")
            return f"Successfully cleared {collection_name}."
        else:
            logger.warning(f"Collection '{collection_name}' does not exist.")
            return "Collection not found."
    except Exception as e:
        log_error_cleanly(e)
        return "Failed to clear knowledge base."
    