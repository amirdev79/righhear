import json

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from users.models import UserProfile, UserSwipeAction
from users.utils import up_to_json, update_device_info, update_user_fb_data
from utils.network import parse_request

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def sign_in(request):
    username, device_info, categories_ids = parse_request(request, ['username', 'deviceInfo'], ['categoriesIds'])
    device_info = json.loads(device_info)
    user, created = User.objects.get_or_create(username=username)
    up, up_created = UserProfile.objects.get_or_create(user=user)
    if up_created:
        print('user created: username - ' + up.user.username)
    else:
        print('user signed in: username - ' + up.user.username)
    user = authenticate(username=username)
    login(request, user)
    if categories_ids:
        up.preferred_categories.clear()
        up.preferred_categories.add(*categories_ids)
    update_device_info(up, device_info)
    up_json = up_to_json(up, request)
    return JsonResponse(up_json)


@csrf_exempt
@login_required
def add_swipe_action(request):
    event_id, action, lat, lng = parse_request(request, ['eventId', 'action', 'lat', 'lng'])
    UserSwipeAction.objects.create(user=request.user.userprofile, event_id=event_id, action=action,
                                   action_time=timezone.now(), lat=lat, lng=lng)
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
    return HttpResponse("Right Hear is a mobile app. Please open the link on your mobile")


@csrf_exempt
@login_required
def invite(request):
    return JsonResponse({'status': 'OK'})


@csrf_exempt
@login_required
def sign_in_with_facebook(request):
    fb_user_id, access_token = parse_request(request, ['userId', 'accessToken'])
    up = request.user.userprofile
    logger.debug('up: ' + up.user.username + ', fb_user_id: ' + str(fb_user_id) + ', access_token: ' + str(access_token))
    up.fb_id = fb_user_id
    up.fb_access_token = access_token
    up.save()
    update_user_fb_data(up)
    up_json = up_to_json(up, request)
    return JsonResponse(up_json)

# EAAEiQAK1MRkBADqY2omBDG0fRQZBJ4f0qAWKXuXfL6ZAacxbEbUd4OBT5Br9MiCsyJQQes5ETdczttOd6G59owxozian0FO8UdeQaytgbeW7ZAW8PjZAkc2dkrs1y4R5QNLGXoSynt7AkzW5Ts5wuxhSfGswYi4w9CjZCoyFOVEkvl67qWU0kvVO5MWQXBmkZAR7t2zYO4mwZDZD
# 10155722070191599
# 319133295391001
# f2bb7b988aaca92f - device id
