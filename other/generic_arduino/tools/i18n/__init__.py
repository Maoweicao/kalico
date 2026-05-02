"""
i18n/__init__.py — Shared internationalization framework
============================================================
Import this module from any tool to enable multilingual support.

Usage:
    from i18n import _, get_option_description, LANGUAGES, set_language

    # Get translated string
    print(_("ui.title"))

    # Switch language
    set_language("zh")

    # Iterate available languages
    for code, info in LANGUAGES.items():
        print(code, info["name"])
"""

_current_language = "en"

# Each language module is lazy-imported on first use.
# Call ``from i18n import en, zh`` or access ``LANGUAGES["en"]["dict"]``
# after loading.
LANGUAGES = {
    "en": {"name": "English",    "name_zh": "英语",   "dict": None},
    "zh": {"name": "简体中文",    "name_zh": "简体中文", "dict": None},
}

# Default language ordering for runtime language toggle.
# The first entry is the default.
LANGUAGE_CODES = ["en", "zh"]


def set_language(code: str) -> None:
    """Switch current language at runtime."""
    global _current_language
    if code not in LANGUAGES:
        code = LANGUAGE_CODES[0]
    _current_language = code


def get_language() -> str:
    """Return the current language code."""
    return _current_language


def _ensure_loaded(code: str):
    """Lazy-load a language dict the first time it's accessed."""
    info = LANGUAGES[code]
    if info["dict"] is not None:
        return info["dict"]
    # Import the language module dynamically
    import importlib

    mod = importlib.import_module(f".{code}", package=__package__)
    info["dict"] = mod.TRANSLATIONS
    return info["dict"]


def _(key: str) -> str:
    """Translate a key to the current language.  Falls back to English
    if the key is missing, and returns the key itself as last resort."""
    # Try current language first
    data = _ensure_loaded(_current_language)
    if key in data:
        return data[key]
    # Fall back to English
    if _current_language != "en":
        data_en = _ensure_loaded("en")
        if key in data_en:
            return data_en[key]
    return key


def get_option_description(opt_name: str, fallback: str) -> str:
    """Get translated description for a config option, or the C comment."""
    trans = _(f"desc.{opt_name}")
    if trans == f"desc.{opt_name}":
        return fallback
    return trans


def toggle_language() -> str:
    """Cycle to the next language, return the new code."""
    global _current_language
    try:
        idx = LANGUAGE_CODES.index(_current_language)
    except ValueError:
        idx = 0
    new_code = LANGUAGE_CODES[(idx + 1) % len(LANGUAGE_CODES)]
    _current_language = new_code
    return new_code
