## Postgres → Milvus Pipeline (POC)

Ingest rows from PostgreSQL, generate text embeddings with FastEmbed, and load them into a Milvus collection using a lightweight `dlt` destination.

### What this includes

- **Docker services**: Milvus Standalone (with etcd + MinIO) and Postgres (pre-seeded `products` table)
- **Pipeline**: `pipelines/postgres_to_milvus.py` reads `products`, embeds text columns, and writes vectors to Milvus

### Prerequisites

- Docker and Docker Compose
- Python 3.13+
- `uv` (recommended) or another modern Python environment manager

Install `uv`:

```bash
pip install uv
```

### Quick start

1. Start infrastructure

```bash
docker compose up -d
```

This starts:

- `milvus-standalone` on `localhost:19530`
- `local-postgres` on `localhost:5432` (user `admin`, password `secret`, db `mydb`)

2. Install Python deps

```bash
uv sync
```

3. Run the pipeline

```bash
uv run python pipelines/postgres_to_milvus.py
```

What it does:

- Creates Milvus collection `product_embeddings_fastembed` (if missing)
- Reads rows from Postgres `products`
- Uses FastEmbed `BAAI/bge-small-en-v1.5` to generate embeddings
- Upserts vectors + metadata into Milvus

### Configuration

The pipeline reads these environment variables (defaults shown):

- `MILVUS_HOST=localhost`
- `MILVUS_PORT=19530`
- `MILVUS_DB_NAME=default`

Optionally create a `.env` file in the repo root:

```bash
echo "MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_DB_NAME=default" > .env
```

### Verifying data in Milvus

We can run a quick check by running test_milvus_data.py in tests directory:

```bash
uv run tests/test_milvus_data.py
```

### Postgres seed data

On startup, Postgres runs `sql/init.sql` which creates a `products` table and inserts a few sample rows.

### Running the FastAPI app (optional)

There is a simple API in `main.py` which we can run by:

```bash
uv run uvicorn main:app --reload
```

#### Dynamic DB connector and querying

This API lets us register any SQL database at runtime and inspect/query it.

- Start the server (as above) and then in another terminal:

Registering a data source:

```bash
curl -s -X POST http://127.0.0.1:8000/configure \
  -H 'Content-Type: application/json' \
  -d '{
        "name": "local",
        "db_url": "postgresql://admin:secret@127.0.0.1:5432/mydb"
      }'
```

Listing table/column metadata for the source:

```bash
curl -s http://127.0.0.1:8000/metadata/local | jq
```

Running an ad-hoc SQL query:

```bash
curl -s -X POST http://127.0.0.1:8000/query/local \
  -H 'Content-Type: application/json' \
  -d '{
        "query": "SELECT id, name, description FROM products LIMIT 5;"
      }' | jq
```

Notes:

- Use any valid SQLAlchemy URL in `db_url` (e.g., Postgres, MySQL, SQLite). Ensure the appropriate DB driver is installed.
- The included Docker Postgres is reachable at `postgresql://admin:secret@127.0.0.1:5432/mydb`.

### Common issues

- **Ports already in use**: Stop any existing Milvus/Postgres, or change the mapped ports in `docker-compose.yml`.
- **Milvus not ready yet**: First startup may take ~1–2 minutes. The pipeline will fail if Milvus is not healthy; wait until `docker compose ps` shows healthy.
- **Reset state**: To wipe local data, stop services and remove volumes:

```bash
docker compose down -v
```

### Repo layout

- `pipelines/postgres_to_milvus.py`: pipeline entrypoint
- `pipelines/milvus.py`: `MilvusStore` helper
- `sql/init.sql`: Postgres schema + seed data
- `docker-compose.yml`: Milvus + Postgres stack
