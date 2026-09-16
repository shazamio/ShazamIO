class FailedDecodeJson(Exception):
    pass


class BadCityName(Exception):
    pass


class BadCountryName(Exception):
    pass


class BadMethod(Exception):
    pass


class BadParseData(Exception):
    pass


class BadResponseStatus(Exception):
    pass


class BadContentType(Exception):
    pass


class BadAppleIds(Exception):
    pass


class RateLimited(BadResponseStatus):
    pass
