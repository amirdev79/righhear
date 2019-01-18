from django.utils import timezone
from django.db.utils import IntegrityError

from users.models import UserDevice


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
