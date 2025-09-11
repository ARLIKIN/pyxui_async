class Exceptions(Exception):
    """
    Базовое исключение для библиотеки pyxui_async.
    :param message: Человеко-читаемое описание ошибки.
    :param error_code: Код ошибки для обработки на стороне клиента.
    """
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"[{self.error_code}] {self.message}."


class NotFound(Exceptions):
    """
    Исключение для ситуации, когда объект не найден (404).
    """
    code = 'NOT_FOUND'
    message = 'Error 404 has been received'

    def __init__(self):
        super().__init__(self.message, self.code)


class BadLogin(Exceptions):
    """
    Исключение для ошибки авторизации (неверный логин/пароль).
    """
    code = 'BAD_LOGIN'
    message = 'Username or password is incorrect'

    def __init__(self):
        super().__init__(self.message, self.code)


class AlreadyLogin(Exceptions):
    """
    Исключение для попытки входа при уже активной сессии.
    """
    code = 'ALREADY_LOGIN'
    message = 'You are currently logged in'

    def __init__(self):
        super().__init__(self.message, self.code)


class Duplicate(Exceptions):
    """
    Исключение для дубликатов при добавлении клиентов.
    """
    code = 'DUPLICATE'

    def __init__(self, message: str):
        super().__init__(message, self.code)


class NoIpRecord(Exceptions):
    """
    Исключение если у клиента нет записей с ip.
    """
    code = 'NO_IP_RECORD'
    message = 'No IP address records were found for the client: {email}'

    def __init__(self, email: str):
        super().__init__(self.message.format(email=email), self.code)
