import dlt
import os
from dlt.sources.sql_database import sql_table
from dlt.common.typing import TDataItems
from dlt.common.schema import TTableSchema
from dotenv import load_dotenv

from fastembed.text import TextEmbedding

from milvus import MilvusStore

load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "default")
MILVUS_URI = f"http://{MILVUS_HOST}:{MILVUS_PORT}"
COLLECTION_NAME = "product_embeddings_fastembed"

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


print(f"Loading lightweight embedding model: {EMBEDDING_MODEL}...")
model = TextEmbedding(model_name=EMBEDDING_MODEL)
EMBEDDING_DIM = model.embedding_size

milvus_store = MilvusStore(uri=MILVUS_URI, db_name=MILVUS_DB_NAME)


@dlt.destination(batch_size=100)
def milvus_destination(items: TDataItems, table: TTableSchema):
    """
    A dlt destination that processes items, generates embeddings using fastembed,
    and loads them into a Milvus collection.
    """
    print(
        f"\n--- Destination received {len(items)} items from table '{table['name']}' ---"
    )

    if not milvus_store.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' not found. Creating...")
        milvus_store.create_collection(
            collection_name=COLLECTION_NAME, dimensions=EMBEDDING_DIM
        )
        milvus_store.client.load_collection(COLLECTION_NAME)

    # identify text columns from the schema
    columns_to_embed = [
        col_name
        for col_name, col_props in table["columns"].items()
        if col_props["data_type"] == "text"
    ]

    if not columns_to_embed:
        print("Warning: No 'text' columns found in the source. Skipping embedding.")
        return

    print(f"Identified columns to embed: {', '.join(columns_to_embed)}")

    texts_to_embed = [
        " ".join(str(item.get(col, "")) for col in columns_to_embed) for item in items
    ]

    print(f"Generating {len(texts_to_embed)} embeddings with fastembed...")

    embeddings_numpy = model.embed(texts_to_embed)
    embeddings = [arr.tolist() for arr in embeddings_numpy]

    # Prepare records for Milvus insertion
    records_to_load = []
    for i, item in enumerate(items):
        record = {
            "source_id": item["id"],
            "dense_vector": embeddings[i],
            "text": texts_to_embed[i][:2000],
        }
        records_to_load.append(record)

    milvus_store.add_vectors(COLLECTION_NAME, records_to_load)


def load_table_products():
    """Defines and runs the dlt pipeline from a PostgreSQL table to Milvus."""
    print("Starting postgres_to_milvus pipeline with fastembed...")
    source = sql_table(table="products")
    pipeline = dlt.pipeline(
        pipeline_name="postgres_to_milvus_fastembed_pipeline",
        destination=milvus_destination,
        dataset_name="product_embeddings_metadata",
    )
    pipeline.run(source)
    print("\nPipeline run finished!")


if __name__ == "__main__":
    load_table_products()
