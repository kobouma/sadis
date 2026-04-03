from django.core.exceptions import ValidationError
import re

def validate_phone_bf(value):
    if not re.match(r'^(\+226)?[0-9]{8}$', value):
        raise ValidationError("Format attendu : 70123456 ou +22670123456")
