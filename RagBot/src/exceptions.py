"""
Domain exceptions.

Rule of thumb: if a failure is something the system can *anticipate* — bad
input, an uncovered module, a dependency that's down — it must be raised as
an AppError subclass. Anything that reaches the caller as a bare Exception
is by definition a bug, and only those should produce "unhandled error".
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base for every anticipated failure."""

    http_status: int = 500
    code: str = "internal_error"
    user_message: str = "خطای داخلی رخ داده است. لطفاً بعداً تلاش کنید."
    retryable: bool = False

    def __init__(
        self,
        detail: str = "",
        *,
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.detail = detail or self.code
        if user_message is not None:
            self.user_message = user_message
        self.context: Dict[str, Any] = context or {}
        super().__init__(self.detail)

    def to_payload(self, trace_id: str = "") -> Dict[str, Any]:
        payload = {
            "code": self.code,
            "message": self.user_message,   # safe to render to the end user
            "detail": self.detail,          # internal; drop this in prod if you prefer
            "retryable": self.retryable,
        }
        if trace_id:
            payload["trace_id"] = trace_id
        return payload


# ---------------------------------------------------------------- 4xx
class EmptyQueryError(AppError):
    http_status, code = 422, "empty_query"
    user_message = "متن سوال خالی است."


class QueryTooLongError(AppError):
    http_status, code = 422, "query_too_long"
    user_message = "سوال شما بسیار طولانی است. لطفاً آن را کوتاه‌تر بنویسید."


class MissingSessionIdError(AppError):
    http_status, code = 422, "missing_session_id"
    user_message = "شناسه گفتگو ارسال نشده است."


class SessionNotFoundError(AppError):
    http_status, code = 404, "session_not_found"
    user_message = "گفتگوی موردنظر یافت نشد."


class DatabaseNotFoundError(AppError):
    http_status, code = 404, "database_not_found"
    user_message = "پایگاه داده موردنظر یافت نشد."


class InvalidDatabaseIdError(AppError):
    http_status, code = 422, "invalid_database_id"
    user_message = "شناسه پایگاه داده معتبر نیست."


class InvalidBusinessObjectError(AppError):
    """The BO document itself is malformed."""
    http_status, code = 422, "invalid_business_object"
    user_message = "ساختار شیء تجاری ارسال‌شده معتبر نیست."


class ModuleNotCoveredError(AppError):
    """The BO is valid, but contains nothing for the requested module."""
    http_status, code = 422, "module_not_covered"
    user_message = "اطلاعات این ماژول در دسترس شما قرار ندارد."


class UnsupportedFileTypeError(AppError):
    http_status, code = 415, "unsupported_file_type"
    user_message = "نوع فایل ارسال‌شده پشتیبانی نمی‌شود."


class NoDocumentsExtractedError(AppError):
    http_status, code = 422, "no_documents_extracted"
    user_message = "از فایل‌های ارسال‌شده هیچ محتوایی استخراج نشد."


# ---------------------------------------------------------------- 5xx
class DependencyError(AppError):
    http_status, code = 503, "dependency_unavailable"
    user_message = "سرویس موقتاً در دسترس نیست. لطفاً دوباره تلاش کنید."
    retryable = True


class VectorStoreError(DependencyError):
    code = "vector_store_unavailable"


class PostgresError(DependencyError):
    code = "database_unavailable"


class LLMUnavailableError(DependencyError):
    code = "llm_unavailable"
    user_message = "سرویس پردازش زبان موقتاً در دسترس نیست. لطفاً دوباره تلاش کنید."


class LLMTimeoutError(LLMUnavailableError):
    http_status, code = 504, "llm_timeout"


class LLMResponseFormatError(AppError):
    """The model answered, but not in the contract we asked for."""
    http_status, code = 502, "llm_bad_response"
    user_message = "پاسخ دریافتی از مدل قابل پردازش نبود. لطفاً دوباره تلاش کنید."
    retryable = True


class DocumentProcessingError(AppError):
    http_status, code = 500, "document_processing_failed"
    user_message = "پردازش فایل‌های ارسال‌شده با خطا مواجه شد."


class ConfigurationError(AppError):
    """Our config is wrong — never the caller's fault, never retryable."""
    http_status, code = 500, "configuration_error"
    user_message = "پیکربندی سرویس ناقص است. لطفاً با پشتیبانی تماس بگیرید."