# HTTP status codes:

ERROR_USER_EXISTS = 412


def parse_request(request, fields, lists=[]):
    if request.method == "POST":
        return [request.POST.get(field) for field in fields] + [request.POST.getlist(l) for l in lists]
