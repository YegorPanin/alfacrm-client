# exceptions.py

class APIClientError(Exception):
    """Базовое исключение для всех ошибок клиента API"""
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message

class AuthenticationError(APIClientError):
    """Ошибка аутентификации (401 Unauthorized)"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)

class AccessDeniedError(APIClientError):
    """Ошибка доступа (403 Forbidden)"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message)

class NotFoundError(APIClientError):
    """Ресурс не найден (404 Not Found)"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)

class RateLimitExceeded(APIClientError):
    """Превышен лимит запросов (429 Too Many Requests)"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message)

class APIRequestError(APIClientError):
    """Общая ошибка API запроса"""
    def __init__(self, message: str, status_code: int, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

class RequestValidationError(APIClientError):
    """Ошибка валидации входных данных"""
    def __init__(self, errors: list, message: str = "Validation error"):
        super().__init__(message)
        self.errors = errors

class MissingBranchError(APIClientError):
    """Не указан обязательный branch_id"""
    def __init__(self, message: str = "Branch ID is required for this operation"):
        super().__init__(message)

class APIConnectionError(APIClientError):
    """Ошибка соединения с API"""
    def __init__(self, message: str = "Connection error"):
        super().__init__(message)
