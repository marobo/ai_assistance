import bleach
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    'p',
    'pre',
    'code',
    'h1',
    'h2',
    'h3',
    'h4',
    'ul',
    'ol',
    'li',
    'blockquote',
    'hr',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
})
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    'code': ['class'],
    'a': ['href', 'title', 'rel'],
}


@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ''
    html = markdown.markdown(
        str(text),
        extensions=['fenced_code', 'tables', 'nl2br'],
    )
    clean = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
    )
    return mark_safe(clean)
