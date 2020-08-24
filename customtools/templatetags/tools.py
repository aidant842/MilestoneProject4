from django import template

register = template.Library()


@register.filter(name='display_price')
def display_price(price):
    return price / 100
