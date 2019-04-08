import csv

from events.models import Artist, Media, EventCategory

MEDIA_URL = 'http://35.196.96.207'
ARTIST_CSV_HEADER = 'id (-), first_name, last_name (leave empty if not relevant), first_name_heb, last_name_heb (leave empty if not relevant), category_id, sub_categories_ids, media1_id , ' \
                    'media1_type, media1_link, media1_playback_start, media1_playback_end, media2_id, media2_type, ' \
                    'media2_link, media2_playback_start, media2_playback_end, media3_id, media3_type, media3_link, ' \
                    'media3_playback_start, media3_playback_end '

ARTIST_FIELDS = ['id (do not touch)', 'first_name', 'last_name', 'first_name_heb', 'last_name_heb', 'image (do not touch)', 'image credits (do not touch)', 'category',
                 'sub_categories', 'media1 id (do not touch)', 'media1 type', 'media1 link/youtube id', 'media1 playback start',
                 'media1 playback end', 'media2 id (do not touch)', 'media2 type', 'media2 link/youtube id', 'media2 playback start',
                 'media2 playback end', 'media3 id (do not touch)', 'media3 type', 'media3 link/youtube id', 'media3 playback start',
                 'media3 playback end']

MEDIA_TYPES = {v: k for k, v in Media.MEDIA_TYPE_CHOICES.items()}


def _cat_to_string(cat):
    return str(cat.id) + ' - ' + cat.title if cat else ''


def _sub_categories_to_str(artist):
    return ','.join([_cat_to_string(sc) for sc in artist.sub_categories.all()])


def _get_media_fields(media):
    return str(media.id), Media.MEDIA_TYPE_CHOICES[media.type], media.link, media.playback_start, media.playback_end


def _get_artist_image_str(artist):
    return MEDIA_URL + artist.image.url if artist.image else ''


def _get_artist_csv_line(artist):
    image = _get_artist_image_str(artist)
    category = artist.category.id if artist.category else ''
    sub_categories = ','.join([str(id) for id in artist.sub_categories.values_list('id', flat=True) or []])

    fields = [str(artist.id), artist.first_name, artist.last_name, artist.first_name_heb, artist.last_name_heb, image, artist.image_credits,
              str(category), sub_categories]
    for media in artist.media.all():
        fields += _get_media_fields(media)

    return ','.join(['"' + (str(val) or '') + '"' for val in fields])


def artists_to_csv(csv_path):
    artists = [_get_artist_csv_line(artist) for artist in Artist.objects.order_by('id')]
    with open(csv_path, 'w+') as f:
        f.write(','.join(ARTIST_FIELDS) + '\n')
        f.write('\n'.join(artists))


def _update_artist_media(artist, media_fields):
    media1_id, media1_type, media1_link, media1_playback_start, media1_playback_end, media2_id, media2_type, media2_link, media2_playback_start, media2_playback_end, media3_id, media3_type, media3_link, media3_playback_start, media3_playback_end = media_fields
    artist.media.clear()
    if media1_id:
        media1 = Media.objects.get(id=media1_id)
        media1.type = MEDIA_TYPES[media1_type]
        media1.link = media1_link
        media1.playback_start = media1_playback_start
        media1.playback_end = media1.playback_end
        media1.save()


def _create_media(type, link, start, end):
    media, created = Media.objects.get_or_create(link=link,
                                                 defaults={'type': MEDIA_TYPES.get(type), 'playback_start': int(start),
                                                           'playback_end': int(end)})
    if not created:
        raise Exception('Media with this link already exists. media id is ' + str(media.id))
    return media


def _update_new_artist_media(artist, media_fields):
    media1_id, media1_type, media1_link, media1_playback_start, media1_playback_end, media2_id, media2_type, media2_link, media2_playback_start, media2_playback_end, media3_id, media3_type, media3_link, media3_playback_start, media3_playback_end = media_fields
    artist.media.clear()
    if media1_id:
        artist.media.add(int(media1_id))
    else:
        media = _create_media(media1_type, media1_link, media1_playback_start, media1_playback_end)
        artist.media.add(media)

    if media2_id:
        artist.media.add(int(media2_id))
    else:
        media = _create_media(media2_type, media2_link, media2_playback_start, media2_playback_end)
        artist.media.add(media)

    if media3_id:
        artist.media.add(int(media3_id))
    else:
        media = _create_media(media3_type, media3_link, media3_playback_start, media3_playback_end)
        artist.media.add(media)


def create_new_artist(fields):
    id, first_name, last_name, first_name_heb, last_name_heb, category_id, sub_categories_ids = fields[:7]
    media_fields = fields[7:]
    artist = Artist.objects.create(first_name=first_name, last_name=last_name, first_name_heb=first_name_heb,
                                   last_name_heb=last_name_heb)
    _update_artist_category(artist, category_id)
    _update_artist_sub_categories(artist, sub_categories_ids)
    _update_new_artist_media(artist, media_fields)


def _add_media(artist, media_fields):
    m_id, m_type, m_link, m_playback_start, m_playback_end = media_fields
    is_youtube = m_type == 'Youtube'
    youtube_id = m_link if is_youtube else None
    link = None if is_youtube else m_link

    if m_id:
        m = Media.objects.get(id=int(m_id))
    else:
        m, created = Media.objects.get_or_create(youtube_id=youtube_id, link=link)
        if not created:
            raise Exception('Media with this link/youtube id already exists. id: ' + str(m.id))
        m.link = link
        m.type=MEDIA_TYPES[m_type]
        m.youtube_id = youtube_id
        m.playback_start = m_playback_start
        m.playback_end = m_playback_end
        m.save()
    artist.media.add(m)


def _update_existing_artist_media(artist, media_fields):
    print('inside update media')
    print(str(media_fields))
    if len(media_fields) == 0:
        return
    else:
        artist.media.clear()
        if len(media_fields) >= 5 and media_fields[1] != '':
            _add_media(artist, media_fields[:5])
        if len(media_fields) >= 10 and media_fields[6] != '':
            _add_media(artist, media_fields[5:10])
        if len(media_fields) >= 15 and media_fields[11] != '':
            _add_media(artist, media_fields[10:15])


def _update_artist_category(artist, category_id):
    if category_id == '':
        raise Exception('Artist ' + str(artist) + ' did not get a category id. quitting..')
    artist.category = EventCategory.objects.get(id=int(category_id))


def _update_artist_sub_categories(artist, sub_categories_ids):
    if sub_categories_ids == '':
        raise Exception('Artist ' + str(artist) + ' did not get any sub categories ids. quitting..')
    artist.sub_categories.clear()
    sc_ids = sub_categories_ids.split(',')
    artist.sub_categories.add(*[int(sc) for sc in sub_categories_ids.split(',')])


def _update_existing_artist(fields):
    id, first_name, last_name, first_name_heb, last_name_heb, image, image_credits, category_id, sub_categories_ids = fields[:8]
    print('first: ' + first_name)
    print('last_name: ' + last_name)
    print('first_name_heb: ' + first_name_heb)
    print('last_name_heb: ' + last_name_heb)
    print('image: ' + image)
    print('category_id: ' + category_id)
    print('sub_categories_ids: ' + sub_categories_ids)
    media_fields = fields[8:]
    print(str(media_fields))
    artist = Artist.objects.get(id=id)
    artist.first_name = first_name
    artist.last_name = last_name
    artist.first_name_heb = first_name_heb
    artist.last_name_heb = last_name_heb
    _update_artist_category(artist, category_id)
    _update_artist_sub_categories(artist, sub_categories_ids)
    _update_existing_artist_media(artist, media_fields)
    artist.save()


def artists_csv_to_db(csv_path):
    with open(csv_path, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for artist_line in reader:
            if reader.line_num == 1:
                continue
            if artist_line[0]:  # artist already exists
                _update_existing_artist(artist_line)
            else:
                create_new_artist(artist_line)
