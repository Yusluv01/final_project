from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value for a given key in a dictionary."""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return ""