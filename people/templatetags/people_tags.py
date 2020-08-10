from django import template

register = template.Library()

@register.filter(name='getkey')
# custom tag to return the value of a dictionary using the supplied key
# used to deal with dictionaries with keys which can't be accessed directly, such as those contaning spaces
def getkey(value, arg):
    return value[arg] if arg in value.keys() else ''