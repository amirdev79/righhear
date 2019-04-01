from events.models import Artist

MEDIA_URL = 'http://35.196.96.207'
ARTIST_CSV_HEADER = 'id, First Name, Last Name, Image, Category, Sub Categories, media1 link, media1 start seconds, media1 end seconds, media2 link, media2 start seconds, media1 end seconds, media3 link, media3 start seconds, media3 end seconds'


def _cat_to_string(cat):
    return str(cat.id) + ' - ' + cat.title if cat else ''


def _sub_categories_to_str(artist):
    return ','.join([_cat_to_string(sc) for sc in artist.sub_categories.all()])


def _media_to_str(artist):
    media1, media2, media3 = '', '', ''
    media = artist.media.all()[:3]
    if len(media) == 3:
        media1, media2, media3 = media
    elif len(media) == 2:
        media1, media2 = media
    elif len(media) == 1:
        media1 = media[0]

    return str(media1), str(media2), str(media3)


def _get_artist_image_str(artist):
    return MEDIA_URL + artist.image.url if artist.image else ''


def _get_artist_csv_line(artist):
    image = _get_artist_image_str(artist)
    category = _cat_to_string(artist.category)
    sub_categories = _sub_categories_to_str(artist)
    media1, media2, media3 = _media_to_str(artist)

    return ','.join(['"' + val + '"' for val in
                     [str(artist.id), artist.first_name, artist.last_name, image, category, sub_categories, media1,
                      media2,
                      media3]])


def artists_to_csv(csv_path):
    artists = [_get_artist_csv_line(artist) for artist in Artist.objects.all()]
    with open(csv_path, 'w+') as f:
        f.write(ARTIST_CSV_HEADER + '\n')
        f.write('\n'.join(artists))
