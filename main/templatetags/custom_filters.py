
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
