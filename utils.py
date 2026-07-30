from importlib import import_module
from typing import Optional

from django.conf import settings
from django.utils.translation import gettext as _


DEFAULT_BASE_TEMPLATE = "base.html"
DEFAULT_HX_TARGET_ID = "main-content"


def _resolve_callable(path: str):
    module_path, func_name = path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, func_name)


def resolve_base_template(request) -> str:
    """Return the base template name.

    Supports either a literal template name via AI_ASSISTANCE_BASE_TEMPLATE
    or a dotted-path callable via AI_ASSISTANCE_BASE_TEMPLATE_FUNC.
    """
    resolver_path: Optional[str] = getattr(
        settings, "AI_ASSISTANCE_BASE_TEMPLATE_FUNC", None
    )
    if resolver_path:
        func = _resolve_callable(resolver_path)
        return func(request)
    return getattr(
        settings,
        "AI_ASSISTANCE_BASE_TEMPLATE",
        DEFAULT_BASE_TEMPLATE,
    )


def resolve_system_prompt(request) -> str:
    """Return the system prompt string.

    If AI_ASSISTANCE_SYSTEM_PROMPT_FUNC is provided (dotted path), call it with
    the request to compute a dynamic prompt. Otherwise use the static
    AI_ASSISTANCE_SYSTEM_PROMPT, falling back to the current default prompt.
    """
    resolver_path: Optional[str] = getattr(
        settings, "AI_ASSISTANCE_SYSTEM_PROMPT_FUNC", None
    )
    if resolver_path:
        func = _resolve_callable(resolver_path)
        return func(request)

    default_prompt = (
        "You are an AI assistant for a Django web application. "
        "Provide helpful, accurate answers relevant to the "
        "application's domain."
    )
    return getattr(
        settings,
        "AI_ASSISTANCE_SYSTEM_PROMPT",
        default_prompt,
    )


def resolve_hx_target_id() -> str:
    return getattr(
        settings,
        "AI_ASSISTANCE_HX_TARGET_ID",
        DEFAULT_HX_TARGET_ID,
    )


def resolve_model_name() -> str:
    return getattr(
        settings,
        "AI_ASSISTANCE_MODEL",
        "openai/gpt-4o-mini",
    )


def resolve_timeout_seconds() -> int:
    return int(getattr(settings, "AI_ASSISTANCE_TIMEOUT", 20))


def resolve_intro_text(request) -> str:
    """Return the intro text shown on the Ask AI page.

    Supports either a literal string via AI_ASSISTANCE_INTRO_TEXT or a
    dotted-path callable via AI_ASSISTANCE_INTRO_TEXT_FUNC that accepts the
    request and returns a string.
    """
    resolver_path: Optional[str] = getattr(
        settings, "AI_ASSISTANCE_INTRO_TEXT_FUNC", None
    )
    if resolver_path:
        func = _resolve_callable(resolver_path)
        return func(request)

    default_intro = (_(
        "Ask me anything about this app. I'm here to help you!"
    ))
    return getattr(settings, "AI_ASSISTANCE_INTRO_TEXT", default_intro)


CHAT_SESSION_KEY = "ai_assistance_chat"
DEFAULT_CHAT_MAX_MESSAGES = 20


def resolve_chat_max_messages() -> int:
    return int(
        getattr(
            settings,
            "AI_ASSISTANCE_CHAT_MAX_MESSAGES",
            DEFAULT_CHAT_MAX_MESSAGES,
        )
    )


def get_chat_history(request) -> list:
    """Return the session chat history as a list of role/content dicts."""
    history = request.session.get(CHAT_SESSION_KEY, [])
    if not isinstance(history, list):
        return []
    return list(history)


def save_chat_history(request, history: list) -> None:
    """Persist chat history in the session, trimmed to the configured max."""
    max_messages = resolve_chat_max_messages()
    request.session[CHAT_SESSION_KEY] = list(history)[-max_messages:]
    request.session.modified = True


def clear_chat_history(request) -> None:
    """Remove chat history from the session."""
    if CHAT_SESSION_KEY in request.session:
        del request.session[CHAT_SESSION_KEY]
        request.session.modified = True
