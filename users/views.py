from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from users.models import UserProfile
from utils.network import parse_request


@csrf_exempt
def login(request):
    username, password = parse_request(request, ['username', 'password'])

    up = UserProfile.objects.get(user__username=username)
    up_json = {'firstName': up.user.first_name,
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

    return JsonResponse(up_json, safe=False)