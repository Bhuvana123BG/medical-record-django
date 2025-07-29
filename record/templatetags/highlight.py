from django import template
import re

register = template.Library()

@register.filter(name='highlight_keywords')
def highlight_keywords(text):
    if not text:
        return ""

    keywords = ['fever', 'pain', 'infection', 'paracetamol', 'diagnosis', 'treatment', 'cold', 'tablet', 'headache']

    for word in keywords:
        pattern = re.compile(rf'\b({re.escape(word)})\b', flags=re.IGNORECASE)
        text = pattern.sub(r'<mark>\1</mark>', text)

    return text
