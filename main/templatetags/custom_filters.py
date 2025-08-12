
from django import template
from django.utils.safestring import mark_safe
import re
from main.utils import time_since_custom

register = template.Library()

@register.filter
def remove_empty_paragraphs(value):
    # Remove empty <p> tags
    cleaned_value = re.sub(r'<p[^>]*>\s*</p>', '&nbsp;', value)
    return mark_safe(cleaned_value)

@register.filter
def time_since(value):
    return time_since_custom(value)

@register.filter
def split(value, delimiter=','):
    """
    Splits the input string by the given delimiter.
    Usage in template: {{ value|split:"," }}
    """
    if not isinstance(value, str):
        return []
    return value.split(delimiter)

@register.filter
def trim(value):
    """
    Trims leading and trailing whitespace from the input string.
    Usage in template: {{ value|trim }}
    """
    if not isinstance(value, str):
        return value
    return value.strip()

@register.filter
def get_color_for_category(category):
    """
    Returns a color code based on the category name.
    Usage in template: {{ category|get_color_for_category }}
    """
    category = category.strip()
    category_colors = {
        'Politics': 'red',
        'Technology': 'purple',
        'Business': 'yellow',
        'Sports': 'green',
        'Entertainment': 'pink',
        'Health': 'red',
        'Science': 'yellow',
        'World': 'blue',
        'Environment': 'blue',
        'Community': 'green',
        'Local': 'blue',
        'Global': 'green',
        'Research': 'purple',
        'Finance': 'yellow'
    }
    
    return category_colors.get(category, '#95a5a6')  # Default color