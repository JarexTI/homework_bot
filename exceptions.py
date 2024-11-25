class EmptyToken(Exception):
    """Ошибка переменной окружения."""


class ServerError(Exception):
    """Ошибки сервера."""


class ClientErorr(Exception):
    """Ошибки клиента."""


class ContentError(Exception):
    """Ошибка контента."""


class StatusError(Exception):
    """Ошибка статуса."""
