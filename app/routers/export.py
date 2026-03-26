from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.models.schemas import ExportRequest
from app.models import store
from app.services.exporter import export_data

router = APIRouter()


@router.post("/download")
async def export_download(request: ExportRequest):
    if not store.get_table(request.table_name):
        raise HTTPException(status_code=404, detail=f"Table '{request.table_name}' not found")

    records = store.get_records(request.table_name)

    if request.filters:
        filtered = []
        for rec in records:
            match = all(
                str(rec.get(k, "")) == str(v) for k, v in request.filters.items()
            )
            if match:
                filtered.append(rec)
        records = filtered

    if request.limit:
        records = records[: request.limit]

    try:
        content, media_type, ext = export_data(records, request.format, request.table_name)
    except ImportError as e:
        raise HTTPException(status_code=501, detail=str(e))

    filename = f"{request.table_name}_export.{ext}"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/formats")
async def list_formats():
    return {
        "formats": [
            {"id": "json", "name": "JSON", "description": "JavaScript Object Notation"},
            {"id": "csv", "name": "CSV", "description": "Comma-Separated Values"},
            {"id": "excel", "name": "Excel", "description": "Microsoft Excel (.xlsx)"},
            {"id": "xml", "name": "XML", "description": "Extensible Markup Language"},
            {"id": "parquet", "name": "Parquet", "description": "Apache Parquet (columnar)"},
        ]
    }