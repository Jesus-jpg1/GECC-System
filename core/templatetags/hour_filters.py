# core/templatetags/hour_filters.py
from django import template

register = template.Library()

@register.filter
def decimal_to_hhmm(decimal_hours):
    """Converte um número decimal de horas para o formato HH:MM."""
    if decimal_hours is None:
        return ""
    
    try:
        hours = int(decimal_hours)
        minutes = int((decimal_hours * 60) % 60)
        return f"{hours:02d}:{minutes:02d}"
    except (ValueError, TypeError):
        return ""