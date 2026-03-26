from faker import Faker
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import random
import uuid
import string

from app.models.schemas import FieldSchema, FieldType, ConstraintType, TableSchema
from app.models import store

fake = Faker()


FAKER_PROVIDER_MAP = {
    "name": lambda: fake.name(),
    "first_name": lambda: fake.first_name(),
    "last_name": lambda: fake.last_name(),
    "email": lambda: fake.email(),
    "phone": lambda: fake.phone_number(),
    "address": lambda: fake.address(),
    "city": lambda: fake.city(),
    "country": lambda: fake.country(),
    "company": lambda: fake.company(),
    "job": lambda: fake.job(),
    "text": lambda: fake.text(max_nb_chars=200),
    "sentence": lambda: fake.sentence(),
    "paragraph": lambda: fake.paragraph(),
    "url": lambda: fake.url(),
    "ipv4": lambda: fake.ipv4(),
    "ipv6": lambda: fake.ipv6(),
    "user_agent": lambda: fake.user_agent(),
    "color": lambda: fake.color_name(),
    "hex_color": lambda: fake.hex_color(),
    "currency_code": lambda: fake.currency_code(),
    "word": lambda: fake.word(),
    "slug": lambda: fake.slug(),
    "username": lambda: fake.user_name(),
    "password": lambda: fake.password(),
    "postcode": lambda: fake.postcode(),
    "street": lambda: fake.street_address(),
    "latitude": lambda: float(fake.latitude()),
    "longitude": lambda: float(fake.longitude()),
    "ssn": lambda: fake.ssn(),
    "iban": lambda: fake.iban(),
    "credit_card": lambda: fake.credit_card_number(),
}


def _generate_unique_value(table_name: str, field: FieldSchema, existing_values: set) -> Any:
    """Generate a value that's not in existing_values."""
    max_attempts = 1000
    for _ in range(max_attempts):
        val = _generate_field_value(table_name, field, None)
        if val not in existing_values:
            return val
    raise ValueError(f"Could not generate unique value for field '{field.name}' after {max_attempts} attempts")


def _generate_field_value(
    table_name: str,
    field: FieldSchema,
    override_datetimes: Optional[Dict[str, str]],
    seed: Optional[int] = None,
) -> Any:
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    ftype = field.type

    # Auto-increment
    if ftype == FieldType.AUTO_INCREMENT or ConstraintType.AUTO_INCREMENT in field.constraints:
        return store.increment_counter(table_name, field.name)

    # UUID
    if ftype == FieldType.UUID:
        return str(uuid.uuid4())

    # Datetime with override
    if ftype in (FieldType.DATETIME, FieldType.DATE):
        if override_datetimes and field.name in override_datetimes:
            return override_datetimes[field.name]
        if field.custom_datetime:
            return field.custom_datetime
        if ftype == FieldType.DATETIME:
            return fake.date_time_between(start_date="-2y", end_date="now").strftime(
                field.datetime_format or "%Y-%m-%dT%H:%M:%S"
            )
        else:
            return fake.date_between(start_date="-2y", end_date="today").strftime("%Y-%m-%d")

    # Email
    if ftype == FieldType.EMAIL:
        return fake.email()

    # Boolean
    if ftype == FieldType.BOOLEAN:
        return random.choice([True, False])

    # Integer
    if ftype == FieldType.INTEGER:
        mn = int(field.min_value) if field.min_value is not None else 1
        mx = int(field.max_value) if field.max_value is not None else 100000
        return random.randint(mn, mx)

    # Float
    if ftype == FieldType.FLOAT:
        mn = field.min_value if field.min_value is not None else 0.0
        mx = field.max_value if field.max_value is not None else 10000.0
        return round(random.uniform(mn, mx), 2)

    # Enum
    if ftype == FieldType.ENUM:
        if field.enum_values:
            return random.choice(field.enum_values)
        return None

    # Nested (unstructured, up to 3 levels)
    if ftype == FieldType.NESTED:
        if field.nested_fields and field.nested_level < 3:
            return {
                nf.name: _generate_field_value(table_name, nf, override_datetimes, seed)
                for nf in field.nested_fields
            }
        return {}

    # String / Text
    if ftype in (FieldType.STRING, FieldType.TEXT):
        if field.faker_provider and field.faker_provider in FAKER_PROVIDER_MAP:
            return FAKER_PROVIDER_MAP[field.faker_provider]()
        # Try to infer from field name
        name_lower = field.name.lower()
        for key, fn in FAKER_PROVIDER_MAP.items():
            if key in name_lower:
                return fn()
        return fake.word() if ftype == FieldType.STRING else fake.text(max_nb_chars=200)

    return None


def generate_records(
    table_schema: TableSchema,
    count: int,
    seed: Optional[int] = None,
    override_datetimes: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)

    table_name = table_schema.name
    generated = []

    # Build pk fields index
    pk_fields = {
        f.name for f in table_schema.fields
        if ConstraintType.PRIMARY_KEY in f.constraints or ConstraintType.UNIQUE in f.constraints
    }

    for _ in range(count):
        record: Dict[str, Any] = {}
        for field in table_schema.fields:
            if field.name in pk_fields:
                existing = store.get_pk_values(table_name, field.name)
                val = _generate_unique_value(table_name, field, existing)
                store.add_pk_value(table_name, field.name, val)
            else:
                val = _generate_field_value(table_name, field, override_datetimes, seed)
            record[field.name] = val
        generated.append(record)

    return generated


def find_pk_field(table_schema: TableSchema) -> Optional[str]:
    for f in table_schema.fields:
        if ConstraintType.PRIMARY_KEY in f.constraints:
            return f.name
    return None


def update_record_by_pk(
    table_name: str,
    pk_field: str,
    pk_value: Any,
    updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    records = store.get_records(table_name)
    for i, rec in enumerate(records):
        rec_pk = rec.get(pk_field)
        # Compare as string to handle type coercion
        if str(rec_pk) == str(pk_value):
            records[i].update(updates)
            store.set_records(table_name, records)
            return records[i]
    return None


def bulk_update_records(
    table_name: str,
    filter_field: str,
    filter_value: Any,
    updates: Dict[str, Any],
) -> int:
    records = store.get_records(table_name)
    updated = 0
    for i, rec in enumerate(records):
        if str(rec.get(filter_field)) == str(filter_value):
            records[i].update(updates)
            updated += 1
    store.set_records(table_name, records)
    return updated