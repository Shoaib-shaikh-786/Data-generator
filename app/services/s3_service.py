from typing import Optional
from app.models.schemas import ExportFormat, S3UploadRequest
from app.services.exporter import export_data
from app.models import store


def upload_to_s3(request: S3UploadRequest) -> dict:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except ImportError:
        raise ImportError("boto3 is required for S3 integration. Install with: pip install boto3")

    table = store.get_table(request.table_name)
    if not table:
        raise ValueError(f"Table '{request.table_name}' not found")

    records = store.get_records(request.table_name)
    content, media_type, ext = export_data(records, request.format, request.table_name)

    key = request.key or f"{request.table_name}/{request.table_name}_export.{ext}"

    session_kwargs = {"region_name": request.aws_region}
    if request.aws_access_key_id:
        session_kwargs["aws_access_key_id"] = request.aws_access_key_id
    if request.aws_secret_access_key:
        session_kwargs["aws_secret_access_key"] = request.aws_secret_access_key

    try:
        session = boto3.Session(**session_kwargs)
        s3_client = session.client("s3")
        s3_client.put_object(
            Bucket=request.bucket,
            Key=key,
            Body=content,
            ContentType=media_type,
        )
        return {
            "success": True,
            "bucket": request.bucket,
            "key": key,
            "size_bytes": len(content),
            "format": request.format,
            "records_uploaded": len(records),
            "s3_uri": f"s3://{request.bucket}/{key}",
        }
    except Exception as e:
        raise RuntimeError(f"S3 upload failed: {str(e)}")


def list_s3_objects(
    bucket: str,
    prefix: str = "",
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_region: str = "us-east-1",
) -> list:
    try:
        import boto3
    except ImportError:
        raise ImportError("boto3 is required for S3 integration.")

    session_kwargs = {"region_name": aws_region}
    if aws_access_key_id:
        session_kwargs["aws_access_key_id"] = aws_access_key_id
    if aws_secret_access_key:
        session_kwargs["aws_secret_access_key"] = aws_secret_access_key

    session = boto3.Session(**session_kwargs)
    s3 = session.client("s3")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    return [
        {
            "key": obj["Key"],
            "size": obj["Size"],
            "last_modified": obj["LastModified"].isoformat(),
            "etag": obj["ETag"],
        }
        for obj in objects
    ]