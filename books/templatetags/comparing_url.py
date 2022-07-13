from django import template

register = template.Library()


@register.simple_tag
def make_comparing_url(url):
    if '?' in url:
        url_with_comparing = url + '&come_from_comparing=1'
    else:
        url_with_comparing = url + '?come_from_comparing=1'

    return url_with_comparing
