from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional
from app.models.schemas import GenerateDataRequest, UpdateRecordRequest, BulkUpdateRequest
from app.models import store
from app.services import generator

router = APIRouter()


@router.post("/generate")
async def generate_data(request: GenerateDataRequest):
    table = store.get_table(request.table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{request.table_name}' not found")

    try:
        records = generator.generate_records(
            table_schema=table,
            count=request.count,
            seed=request.seed,
            override_datetimes=request.override_datetimes,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    store.append_records(request.table_name, records)
    return {
        "message": f"Generated {len(records)} records for table '{request.table_name}'",
        "count": len(records),
        "records": records,
    }


@router.get("/{table_name}")
async def get_data(
    table_name: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=1000),
    sort_by: Optional[str] = None,
    sort_desc: bool = False,
):
    if not store.get_table(table_name):
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    records = store.get_records(table_name)

    if sort_by:
        try:
            records = sorted(records, key=lambda r: r.get(sort_by, ""), reverse=sort_desc)
        except Exception:
            pass

    total = len(records)
    start = (page - 1) * page_size
    end = start + page_size
    page_records = records[start:end]

    return {
        "table_name": table_name,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size if total > 0 else 0,
        "records": page_records,
    }


@router.get("/{table_name}/stats")
async def get_table_stats(table_name: str):
    if not store.get_table(table_name):
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    records = store.get_records(table_name)
    table = store.get_table(table_name)
    return {
        "table_name": table_name,
        "total_records": len(records),
        "fields_count": len(table.fields),
        "is_structured": table.is_structured,
    }


@router.put("/record/update")
async def update_record(request: UpdateRecordRequest):
    table = store.get_table(request.table_name)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{request.table_name}' not found")

    pk_field = generator.find_pk_field(table)
    if not pk_field:
        raise HTTPException(
            status_code=422,
            detail="No primary key defined for this table. Cannot update by record ID.",
        )

    updated = generator.update_record_by_pk(
        table_name=request.table_name,
        pk_field=pk_field,
        pk_value=request.record_id,
        updates=request.updates,
    )
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Record with {pk_field}={request.record_id} not found",
        )
    return {"message": "Record updated", "record": updated}


@router.put("/record/bulk-update")
async def bulk_update(request: BulkUpdateRequest):
    if not store.get_table(request.table_name):
        raise HTTPException(status_code=404, detail=f"Table '{request.table_name}' not found")

    count = generator.bulk_update_records(
        table_name=request.table_name,
        filter_field=request.filter_field,
        filter_value=request.filter_value,
        updates=request.updates,
    )
    return {"message": f"Updated {count} records", "updated_count": count}


@router.delete("/{table_name}/{record_index}")
async def delete_record(table_name: str, record_index: int):
    if not store.get_table(table_name):
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    records = store.get_records(table_name)
    if record_index < 0 or record_index >= len(records):
        raise HTTPException(status_code=404, detail="Record index out of range")
    removed = records.pop(record_index)
    store.set_records(table_name, records)
    return {"message": "Record deleted", "record": removed}


@router.post("/{table_name}/add")
async def add_single_record(table_name: str, record: Dict[str, Any]):
    if not store.get_table(table_name):
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    store.append_records(table_name, [record])
    return {"message": "Record added", "record": record}