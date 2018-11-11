def up_to_json(up, request):
    return {'firstName': up.user.first_name,
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
