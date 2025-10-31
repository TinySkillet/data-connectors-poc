from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530", db_name="default")
col = "product_embeddings_fastembed"
print("Has collection?", client.has_collection(col))
if client.has_collection(col):
    stats = client.get_collection_stats(col)
    print("Collection stats:", stats)
