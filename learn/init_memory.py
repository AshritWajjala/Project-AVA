from qdrant_client import QdrantClient

client = QdrantClient(url="http://127.0.0.1:6333")

model_name = "BAAI/bge-small-en-v1.5"

embedding_size = client.get_embedding_size(model_name)

client.set_model(model_name)

client.recreate_collection(
    collection_name="buddy_memories",
    vectors_config=client.get_fastembed_vector_params() 
)

memories = [
    "User's name is Ashrit.",
    "Ashrit is a Computer Science Master's graduate.",
    "Ashrit lives in Hyderabad/Bangalore and is looking for AI/ML roles.",
    "Ashrit's current weight is 112.4kg, and his goal is 85-90kg.",
    "Ashrit's PC has an NVIDIA RTX 5080 and an AMD Ryzen 7 7800X3D.",
    "Ashrit is learning Pop!_OS and Linux."
]

client.add(
    collection_name="buddy_memories",
    documents=memories,
    ids=range(len(memories))
)

# Quick Test Search
search_result = client.query(
    collection_name="buddy_memories",
    query_text="What GPU do I have?",
    limit=1
)
print(f"Search Result: {search_result[0].document}")