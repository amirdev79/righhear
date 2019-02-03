# HTTP status codes:
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

ERROR_USER_EXISTS = 412


def parse_request(request, fields=[], lists=[]):
    if request.method == "POST":
        return [request.POST.get(field) for field in fields] + [request.POST.getlist(l) for l in lists]
    else:
        return [request.GET.get(field) for field in fields] + [request.GET.getlist(l) for l in lists]


class PasswordlessAuthBackend(ModelBackend):
    """Log in to Django without providing a password.

    """
    def authenticate(self, request, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


