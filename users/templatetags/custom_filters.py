from django import template

register = template.Library()

@register.filter
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter
def getattribute(obj, attr):
    """Gets a form field by its name"""
    if hasattr(obj, attr):
        field = getattr(obj, attr)
        return field
    return obj[attr] if attr in obj else ''

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)