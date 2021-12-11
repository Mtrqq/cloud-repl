from crepl.settings import settings


def is_supported_lang(language: str) -> bool:
    return language in settings.AVAILABLE_LANGUAGES


def get_endpoint_for_lang(base_url: str, language: str) -> str:
    if not is_supported_lang(language):
        raise ValueError("Unsupported language")

    return base_url.rstrip("/") + "/" + language
