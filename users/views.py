import json

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
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
    user = authenticate(username=username)
    login(request, user)
    up.preferred_categories.clear()
    up.preferred_categories.add(*categories_ids)
    update_device_info(up ,device_info)
    up_json = up_to_json(up, request)
    return JsonResponse(up_json)


@csrf_exempt
@login_required
def add_swipe_action(request):
    event_id, action = parse_request(request, ['eventId', 'action'])
    UserSwipeAction.objects.create(user=request.user.userprofile, event_id=event_id, action=action, action_time=timezone.now())
    return HttpResponse()


@csrf_exempt
@login_required
def update_user_profile(request):
    lang_code, categories_ids = parse_request(request, ['langCode'], lists=['categoriesIds'])
    up = UserProfile.objects.get(user=request.user)
    if categories_ids:
        up.preferred_categories.clear()
        up.preferred_categories.add(*categories_ids)
    if lang_code:
        up.preferred_language = lang_code
        up.save()
    up_json = up_to_json(up, request)
    return JsonResponse(up_json)


def landing_page(request):
    return HttpResponse("App landing page")


@csrf_exempt
@login_required
def invite(request):
    return JsonResponse({'status': 'OK'})
