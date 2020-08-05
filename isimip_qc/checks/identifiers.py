import jsonschema

from ..config import settings


def check_schema(file):
    if file.identifiers:
        try:
            jsonschema.validate(schema=settings.SCHEMA, instance=file.identifiers)
        except jsonschema.exceptions.ValidationError as e:
            file.error('Failed to validate with JSON schema: %s\n%s', file.identifiers, e)
