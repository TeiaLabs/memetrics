class MemetricsClientError(Exception):
    pass


class MissingAPIKeyError(MemetricsClientError):
    pass


class MissingAPIURLError(MemetricsClientError):
    pass
