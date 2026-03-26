from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import TableSchema, TableSchemaUpdate
from app.models import store

router = APIRouter()


@router.get("/", response_model=List[str])
async def list_tables():
    return store.list_tables()


@router.post("/", response_model=TableSchema, status_code=201)
async def create_table(schema: TableSchema):
    if store.get_table(schema.name):
        raise HTTPException(status_code=409, detail=f"Table '{schema.name}' already exists")
    store.save_table(schema)
    return schema


@router.get("/{table_name}", response_model=TableSchema)
async def get_table(table_name: str):
    table = store.get_table(table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    return table


@router.put("/{table_name}", response_model=TableSchema)
async def update_table(table_name: str, update: TableSchemaUpdate):
    table = store.get_table(table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    data = table.model_dump()
    if update.description is not None:
        data["description"] = update.description
    if update.fields is not None:
        data["fields"] = [f.model_dump() for f in update.fields]
    if update.is_structured is not None:
        data["is_structured"] = update.is_structured
    updated = TableSchema(**data)
    store.save_table(updated)
    return updated


@router.delete("/{table_name}")
async def delete_table(table_name: str):
    if not store.delete_table(table_name):
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    return {"message": f"Table '{table_name}' deleted"}


@router.post("/{table_name}/clear")
async def clear_table_data(table_name: str):
    if not store.get_table(table_name):
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    store.clear_records(table_name)
    return {"message": f"All data cleared for table '{table_name}'"}