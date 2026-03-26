from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    EMAIL = "email"
    UUID = "uuid"
    AUTO_INCREMENT = "auto_increment"
    ENUM = "enum"
    TEXT = "text"
    NESTED = "nested"


class ConstraintType(str, Enum):
    PRIMARY_KEY = "primary_key"
    UNIQUE = "unique"
    NOT_NULL = "not_null"
    AUTO_INCREMENT = "auto_increment"


class FieldSchema(BaseModel):
    name: str
    type: FieldType
    constraints: List[ConstraintType] = []
    default: Optional[Any] = None
    enum_values: Optional[List[str]] = None
    datetime_format: Optional[str] = "%Y-%m-%dT%H:%M:%S"
    custom_datetime: Optional[str] = None  # Fixed datetime value
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    faker_provider: Optional[str] = None  # e.g. "name", "address", "company"
    # For nested (unstructured) fields up to 3 levels
    nested_fields: Optional[List["FieldSchema"]] = None
    nested_level: int = 0  # 0=top, 1=sub, 2=sub-sub, 3=sub-sub-sub


FieldSchema.model_rebuild()


class TableSchema(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[FieldSchema]
    is_structured: bool = True


class TableSchemaUpdate(BaseModel):
    description: Optional[str] = None
    fields: Optional[List[FieldSchema]] = None
    is_structured: Optional[bool] = None


class GenerateDataRequest(BaseModel):
    table_name: str
    count: int = Field(default=10, ge=1, le=10000)
    seed: Optional[int] = None
    override_datetimes: Optional[Dict[str, str]] = None  # field_name -> datetime str


class UpdateRecordRequest(BaseModel):
    table_name: str
    record_id: Any  # primary key value
    updates: Dict[str, Any]


class BulkUpdateRequest(BaseModel):
    table_name: str
    filter_field: str
    filter_value: Any
    updates: Dict[str, Any]


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PARQUET = "parquet"
    XML = "xml"


class ExportRequest(BaseModel):
    table_name: str
    format: ExportFormat = ExportFormat.JSON
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None


class S3UploadRequest(BaseModel):
    table_name: str
    bucket: str
    key: Optional[str] = None
    format: ExportFormat = ExportFormat.JSON
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"


class S3Config(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    bucket: str


class DataRecord(BaseModel):
    data: Dict[str, Any]


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 50