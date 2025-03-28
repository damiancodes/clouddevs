from django import template
import datetime

register = template.Library()

@register.filter
def abs_value(value):
    return abs(value)

# You can add more custom filters here if needed
@register.filter
def subtract(value, arg):
    return value - arg