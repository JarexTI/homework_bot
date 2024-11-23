class ServerError(Exception):
    """Ошибки сервера."""

    pass


class ClientErorr(Exception):
    """Ошибки клиента."""

    pass


class ContentError(Exception):
    """Ошибка контента."""

    pass


class StatusError(Exception):
    """Ошибка статуса."""

    pass
