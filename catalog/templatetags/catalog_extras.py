"""
Custom template tag: query_replace

"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_replace(context, **kwargs):
    """
    Return the current query string with the given key(s) updated.

    Example:
        Current URL: /products/?query=wireless&category=2&page=1
        {% query_replace page=2 %} → query=wireless&category=2&page=2
    """
    request = context.get("request")
    if not request:
        return ""

    # Copy the current GET params so we can mutate them
    params = request.GET.copy()

    for key, value in kwargs.items():
        params[key] = value

    return params.urlencode()
