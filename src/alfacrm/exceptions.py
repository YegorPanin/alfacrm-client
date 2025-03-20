class ALFACRMError(Exception):
    """Базовое исключение для всех ошибок ALFA CRM"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)

class AuthenticationError(ALFACRMError):
    """Ошибка аутентификации (неверный токен или ключ)"""

class APIRequestError(ALFACRMError):
    """Ошибка при выполнении запроса к API"""
    def __init__(self, message: str, response_data: dict = None):
        self.response_data = response_data
        super().__init__(message)

class NotFoundError(APIRequestError):
    """Запрошенный ресурс не найден"""

class RateLimitExceeded(APIRequestError):
    """Превышен лимит запросов"""

class ValidationError(ALFACRMError):
    """Ошибка валидации входных данных"""