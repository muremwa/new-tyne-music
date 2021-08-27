from django import template

register = template.Library()


@register.filter
def album_artists(artists):
    names = [artist.name for artist in artists.all()]
    count = len(names)

    if count < 1:
        name = 'No Artist'

    elif count == 1:
        name = names[0]

    elif count == 2:
        name = ' & '.join(names)

    elif 2 < count < 5:
        name = ', '.join(names)

    else:
        name = 'Various Artists'

    return name


@register.filter
def album_artists_string(artists):
    return ', '.join([artist.name for artist in artists.all()])
