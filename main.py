from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import sqlalchemy

app = FastAPI()
data_sources: Dict[str, str] = {}


class DataSourceConfig(BaseModel):
    name: str
    db_url: str


@app.post("/configure")
def configure_source(config: DataSourceConfig):
    data_sources[config.name] = config.db_url
    return {"message": f"Data source {config.name} configured."}


@app.get("/metadata/{source_name}")
def get_metadata(source_name: str):
    db_url = data_sources.get(source_name)
    if not db_url:
        raise HTTPException(status_code=404, detail="Data source not found")

    engine = sqlalchemy.create_engine(db_url)
    meta = sqlalchemy.MetaData()
    meta.reflect(bind=engine)
    schemas = {}
    for table_name, table in meta.tables.items():
        schemas[table_name] = [c.name for c in table.columns]
    return schemas


class SQLQuery(BaseModel):
    query: str


@app.post("/query/{source_name}")
def run_query(source_name: str, payload: SQLQuery):
    db_url = data_sources.get(source_name)
    if not db_url:
        raise HTTPException(status_code=404, detail="Data source not found")

    engine = sqlalchemy.create_engine(db_url)
    with engine.connect() as connection:
        try:
            result = connection.execute(sqlalchemy.text(payload.query))
            rows = [dict(row._mapping) for row in result]
            return {"rows": rows}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


# You can now run this FastAPI app with: uvicorn main:app --reload
