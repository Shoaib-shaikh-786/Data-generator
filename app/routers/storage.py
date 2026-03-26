from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.schemas import S3UploadRequest
from app.services.s3_service import upload_to_s3, list_s3_objects

router = APIRouter()


@router.post("/s3/upload")
async def s3_upload(request: S3UploadRequest):
    try:
        result = upload_to_s3(request)
        return result
    except ImportError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/s3/list")
async def s3_list(
    bucket: str = Query(...),
    prefix: str = Query(default=""),
    aws_access_key_id: Optional[str] = Query(default=None),
    aws_secret_access_key: Optional[str] = Query(default=None),
    aws_region: str = Query(default="us-east-1"),
):
    try:
        objects = list_s3_objects(
            bucket=bucket,
            prefix=prefix,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
        )
        return {"bucket": bucket, "prefix": prefix, "objects": objects, "count": len(objects)}
    except ImportError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))