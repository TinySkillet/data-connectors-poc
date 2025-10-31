## 1. Configure the Postgres Source

```
curl -X POST "http://localhost:8000/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_pg",
    "db_url": "postgresql+psycopg2://admin:secret@localhost:5432/mydb"
  }'
```

2. Get Table Metadata

```
curl "http://localhost:8000/metadata/my_pg"
```

3. Query Example (first 5 rows from products table):

```
curl -X POST "http://localhost:8000/query/my_pg" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM products LIMIT 5"
  }'
```
