# HTTP status codes:

ERROR_USER_EXISTS = 412

def parse_request(request, fields):

    if request.method == "POST":
        return (request.POST.get(field) for field in fields)