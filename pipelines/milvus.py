import os
from typing import Dict, List
from pymilvus import (
    MilvusClient,
    FieldSchema,
    DataType,
    CollectionSchema,
)
from dotenv import load_dotenv

load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
DB_NAME = os.getenv("MILVUS_DB_NAME", "default")


class MilvusStore:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = MilvusClient(uri=self.uri, db_name=self.db_name)

    def has_collection(self, collection_name: str) -> bool:
        return self.client.has_collection(collection_name)

    def create_collection(self, collection_name: str, dimensions: int):
        schema = self._construct_schema(dim=dimensions)
        self.client.create_collection(collection_name=collection_name, schema=schema)

        index_params = self.client.prepare_index_params(
            field_name="dense_vector",
            index_type="AUTOINDEX",
            metric_type="IP",
        )
        self.client.create_index(collection_name, index_params)
        print(f"Collection '{collection_name}' created and indexed.")

    def add_vectors(self, collection_name: str, data: List[Dict]) -> int:
        if not data:
            return 0

        # Extract all source_ids
        source_ids = [d["source_id"] for d in data if "source_id" in d]

        # Delete existing vectors with same source_ids only if there are any
        if source_ids:
            expr = f"source_id in [{','.join(str(sid) for sid in source_ids)}]"
            del_res = self.client.delete(collection_name, expr=expr)
            print(f"Deleted records with source_ids: {source_ids}")
        else:
            print("No source_ids to delete, skipping delete step.")

        # Insert new/updated vectors
        res = self.client.insert(collection_name=collection_name, data=data)
        self.client.flush(collection_name=collection_name)
        print(f"Inserted {res['insert_count']} records. PKs: {res['ids'][:5]}...")
        return res["insert_count"]

    def _construct_schema(self, dim: int) -> CollectionSchema:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="source_id", dtype=DataType.INT64),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        ]
        return CollectionSchema(fields=fields, description="Product embeddings")
