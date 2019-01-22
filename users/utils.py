import facebook
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.utils import IntegrityError

from users.models import UserDevice, UserData, FacebookEvent


def up_to_json(up, request):
    return {'id': up.id,
            'firstName': up.user.first_name,
            'lastName': up.user.last_name,
            'username': up.user.username,
            'categories': [{
                'title': c.title,
                'image': request.build_absolute_uri(c.image.url) if c.image else ''}
                for c in up.preferred_categories.all()],
            'subCategories': [{
                'categoryId': sc.id,
                'title': sc.title,
                'image': request.build_absolute_uri(sc.image.url) if sc.image else ''} for sc in
                up.preferred_sub_categories.all()]}


def update_device_info(up, device_info):
    _di = lambda key: device_info.get(key)

    ud_defatuls = {'os': _di('os'),
                   'os_version': _di('osVersion'),
                   'model': _di('model'),
                   'timezone': _di('timezone'),
                   'push_token': _di('pushToken'),
                   'last_login': timezone.now(),
                   'user': up}
    try:
        ud, created = UserDevice.objects.update_or_create(device_id=_di('deviceId'), defaults=ud_defatuls)
    except IntegrityError:
        pass


def _update_user_fb_events(up, events):
    ud_fb_events = []
    for event in events:
        defaults = {'name': event['name'], 'description': event['description'], 'start_time': event['start_time'], 'end_time': event['end_time'], 'place': event['place']}
        fe, created = FacebookEvent.objects.get_or_create(fb_id=event['id'], defaults=defaults)
        ud_fb_events.append(fe)
    up.user_data.fb_events.add(*ud_fb_events)


def _update_user_fb_friends(up, friends):
    pass


def _update_user_fb_profile_images(up, small, normal, large):
    ext = '.jpg' if small['mime-type'] == 'image/jpeg' else '.png'
    up.user_data.fb_profile_image_small = ContentFile(small['data'], name='profiles/{0}/{1}'.format(up.id, 'fb_profile_image_small' + ext))
    up.user_data.fb_profile_image_normal = ContentFile(normal['data'], name='profiles/{0}/{1}'.format(up.id, 'fb_profile_image_normal' + ext))
    up.user_data.fb_profile_image_large = ContentFile(large['data'], name='profiles/{0}/{1}'.format(up.id, 'fb_profile_image_large' + ext))
    up.user_data.save()


def update_user_fb_data(up):
    graph = facebook.GraphAPI(access_token=up.fb_access_token)
    args = {'fields': 'id,name,first_name,last_name,middle_name,picture'}
    basic_fb_data = graph.get_object('me', **args)
    profile_picture_small = graph.get_object(id='me/picture', type='small')
    profile_picture_normal = graph.get_object(id='me/picture', type='normal')
    profile_picture_large = graph.get_object(id='me/picture', type='large')
    events = graph.get_connections(id='me', connection_name='events')
    friends = graph.get_connections(id='me', connection_name='friends')
    up.user.first_name, up.user.last_name = basic_fb_data.get('first_name'), basic_fb_data.get('last_name')
    up.user.save()
    UserData.objects.get_or_create(userprofile=up)
    _update_user_fb_profile_images(up, profile_picture_small, profile_picture_normal, profile_picture_large)
    _update_user_fb_events(up, events['data'])
    _update_user_fb_friends(up, friends['data'])