def underscore_to_camelcase(value):
    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(next(c)(x) if x else '_' for x in value.split("_"))


def values_to_camelcase(values):
    return [{underscore_to_camelcase(key): item[key] for key in item} for item in values]