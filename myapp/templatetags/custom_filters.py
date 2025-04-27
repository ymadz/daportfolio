from django import template
import json
from decimal import Decimal

register = template.Library()

@register.filter
def pluck(queryset, key):
    """Extracts values from queryset for Chart.js"""
    result = []
    for item in queryset:
        value = item.get(key, "Unknown")
        if isinstance(value, Decimal):
            value = float(value)
        result.append(value)
    return json.dumps(result)
