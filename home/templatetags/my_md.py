from django.template import Library
import markdown
register = Library()

@register.filter
def md(value):
    return markdown.markdown(value)