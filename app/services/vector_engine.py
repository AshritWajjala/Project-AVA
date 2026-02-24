from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from app.core.config import settings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                   model_kwargs={'device': 'cpu'})

client = QdrantClient(url="http://127.0.0.1:6333")

def index_pdf(filepath, collection_name='research_papers'):
    docs = PyPDFLoader(file_path=filepath).load()
    split_docs = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(documents=docs)
        
    # client.recreate_collection(
    # collection_name="buddy_memories",
    # vectors_config=client.get_fastembed_vector_params() 
    # )
    
    # client.add(
    #     collection_name=collection_name,
    #     documents=split_docs,
    #     ids=range(len(split_docs))
    # )

    vectorstore = QdrantVectorStore.from_documents(
            client=client,
            embedding=embeddings, 
            documents=split_docs,
            path="./data/qdrant_db",
            collection_name=collection_name,
        )
    

def query_research(question, collection_name="research_papers"):
    vector_store = QdrantVectorStore.from_existing_collection(
        client=client,
        embedding=embeddings,
        path='./data/qdrant_db',
        collection_name=collection_name
    )
    
    # Returning top 3 results
    results = vector_store.similarity_search(query=question, k=3)
    
    # Combine results into one string for AVA's context
    context = "\n\n".join([doc.page_content for doc in results])
    
    return context

def clear_research_collection(collection_name="research_papers"):
    """Wipes out entire collection data

    Args:
        collection_name (str, optional): name of the collection. Defaults to "research_papers".
    """
    if client.collection_exists(collection_name=collection_name):
        client.delete_collection(collection_name=collection_name)
    