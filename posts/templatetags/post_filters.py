from django import template

register = template.Library()

@register.filter
def limit_comments(comments, limit=3):
    """Limit the number of comments displayed"""
    try:
        return comments[:int(limit)]
    except (ValueError, TypeError):
        return comments[:3]

@register.filter  
def truncate_text(text, length=100):
    """Truncate text to specified length"""
    try:
        length = int(length)
        if len(str(text)) > length:
            return str(text)[:length] + "..."
        return str(text)
    except (ValueError, TypeError):
        return str(text)