from typing import Any, Dict, List, Optional
from app.models.schemas import TableSchema
import threading

_lock = threading.Lock()

# table_name -> TableSchema
tables: Dict[str, TableSchema] = {}

# table_name -> List[Dict[str, Any]]
records: Dict[str, List[Dict[str, Any]]] = {}

# table_name -> set of primary key values (for uniqueness enforcement)
primary_key_values: Dict[str, Dict[str, set]] = {}

# table_name -> auto_increment counters per field
auto_increment_counters: Dict[str, Dict[str, int]] = {}


def get_table(name: str) -> Optional[TableSchema]:
    return tables.get(name)


def save_table(schema: TableSchema):
    with _lock:
        tables[schema.name] = schema
        if schema.name not in records:
            records[schema.name] = []
        if schema.name not in primary_key_values:
            primary_key_values[schema.name] = {}
        if schema.name not in auto_increment_counters:
            auto_increment_counters[schema.name] = {}


def delete_table(name: str) -> bool:
    with _lock:
        if name not in tables:
            return False
        del tables[name]
        records.pop(name, None)
        primary_key_values.pop(name, None)
        auto_increment_counters.pop(name, None)
        return True


def get_records(name: str) -> List[Dict[str, Any]]:
    return records.get(name, [])


def set_records(name: str, data: List[Dict[str, Any]]):
    with _lock:
        records[name] = data


def append_records(name: str, new_records: List[Dict[str, Any]]):
    with _lock:
        if name not in records:
            records[name] = []
        records[name].extend(new_records)


def clear_records(name: str):
    with _lock:
        records[name] = []
        primary_key_values[name] = {}
        auto_increment_counters[name] = {}


def get_pk_values(table_name: str, field_name: str) -> set:
    return primary_key_values.get(table_name, {}).get(field_name, set())


def add_pk_value(table_name: str, field_name: str, value: Any):
    with _lock:
        if table_name not in primary_key_values:
            primary_key_values[table_name] = {}
        if field_name not in primary_key_values[table_name]:
            primary_key_values[table_name][field_name] = set()
        primary_key_values[table_name][field_name].add(value)


def get_counter(table_name: str, field_name: str) -> int:
    return auto_increment_counters.get(table_name, {}).get(field_name, 0)


def increment_counter(table_name: str, field_name: str) -> int:
    with _lock:
        if table_name not in auto_increment_counters:
            auto_increment_counters[table_name] = {}
        current = auto_increment_counters[table_name].get(field_name, 0)
        auto_increment_counters[table_name][field_name] = current + 1
        return current + 1


def list_tables() -> List[str]:
    return list(tables.keys())