import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from users.models import UserProfile, UserDevice, UserSwipeAction
from users.utils import up_to_json
from utils.network import parse_request, ERROR_USER_EXISTS


@csrf_exempt
def login(request):
    username, password = parse_request(request, ['username', 'password'])

    up = UserProfile.objects.get(user__username=username)
    up_json = up_to_json(up, request)

    return JsonResponse(up_json, safe=False)


@csrf_exempt
def register(request):
    username, device_info, categories_ids = parse_request(request, ['username', 'deviceInfo', 'categoriesIds'])
    print('device info: ' + device_info)
    device_info = json.loads(device_info)
    user, created = User.objects.get_or_create(username=username)
    if not created:
        return HttpResponse(status=ERROR_USER_EXISTS)
    up = UserProfile.objects.create(user=user)
    up.preferred_categories.add(categories_ids)

    _di = lambda key: device_info.get(key)

    ud_defatuls = {'os': _di('os'),
                   'os_version': _di('osVersion'),
                   'model': _di('model'),
                   'timezone': _di('timezone'),
                   'push_token': _di('pushToken'),
                   'last_login': timezone.now(),
                   'user': up}
    ud, created = UserDevice.objects.get_or_create(device_id= device_info.get('deviceId'), defaults=ud_defatuls)
    print ('created:' + str(created))
    # User = User.objects.get_or_create(username='email', )
    up_json = up_to_json(up, request)
    return JsonResponse(up_json)


def add_swipe_action(request):
    username, event_id, action = parse_request(request, ['username', 'eventId', 'action'])
    UserSwipeAction.objects.create(user = request.user.userprofile, event_id=int(event_id), action=action, action_time=timezone.now())
    return HttpResponse()