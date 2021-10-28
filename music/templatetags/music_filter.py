from django.template import Library
from django.utils import timesince, timezone

register = Library()


@register.filter
def album_artists(artists, q_set=True):
    artists = artists.all() if bool(q_set) else artists
    names = [artist.name for artist in artists]
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


@register.filter
def release_date_to(release_date):
    stamp = ''

    if release_date:
        if release_date > timezone.now().date():
            stamp = f'Pre-release: {timesince.timeuntil(release_date)} to go'
        else:
            stamp = f'{timesince.timesince(release_date)} ago'
    return stamp


@register.filter
def full_release(release_date):
    return release_date.strftime('%A %B %d, %Y') if release_date else ''
