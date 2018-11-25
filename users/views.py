import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from users.models import UserProfile, UserSwipeAction
from users.utils import up_to_json, update_device_info
from utils.network import parse_request


@csrf_exempt
def sign_in(request):
    username, device_info, categories_ids = parse_request(request, ['username', 'deviceInfo'], ['categoriesIds'])
    device_info = json.loads(device_info)
    user, created = User.objects.get_or_create(username=username)
    up, up_created = UserProfile.objects.get_or_create(user=user)
    if up_created:
        print ('user created: username - ' + up.user.username)
    else:
        print ('user signed in: username - ' + up.user.username)
    up.preferred_categories.clear()
    up.preferred_categories.add(*categories_ids)
    update_device_info(up ,device_info)
    up_json = up_to_json(up, request)
    return JsonResponse(up_json)


def add_swipe_action(request):
    username, event_id, action = parse_request(request, ['username', 'eventId', 'action'])
    UserSwipeAction.objects.create(user = request.user.userprofile, event_id=int(event_id), action=action, action_time=timezone.now())
    return HttpResponse()