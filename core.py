import httpx
from typing import List, Optional
from decouple import config


DEFAULT_MODEL = config(
    "OPENROUTER_MODEL",
    default="openai/gpt-4o-mini",
)


def ask_ai(
    prompt: str,
    *,
    api_key: Optional[str],
    system_prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = 20,
    history: Optional[List[dict]] = None,
) -> str:
    """Call the OpenRouter API with the given parameters and return the text.

    This function is framework-agnostic and contains no Django imports.
    All configuration must be passed in explicitly by the caller.

    ``history`` is an optional list of prior turns, each a dict with
    ``role`` (``user`` or ``assistant``) and ``content``. The new ``prompt``
    is appended as the latest user message.
    """

    if not prompt.strip():
        return ""

    if not api_key:
        return (
            "AI service is currently unavailable. "
            "Please contact the administrator to "
            "configure the API key."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json",
    }

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for msg in history:
            role = msg.get("role")
            content = (msg.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": prompt})

    json_data = {
        "model": model,
        "max_tokens": 300,
        "messages": messages,
    }

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=json_data,
            timeout=timeout_seconds,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get(
                "content",
                "No reply received from AI.",
            )
        if response.status_code == 401:
            return (
                "AI service authentication failed. "
                "Please check the API key configuration."
            )
        if response.status_code == 429:
            return (
                "AI service is currently busy. "
                "Please try again in a few moments."
            )
        try:
            error = response.json()
            return f"Status {response.status_code}: {error}"
        except Exception:
            return f"Status {response.status_code}: {response.text}"

    except httpx.TimeoutException:
        return "AI service request timed out. Please try again."
    except httpx.RequestError as e:
        return f"AI service connection error: {str(e)}"
    except Exception as e:  # noqa: BLE001 - surface unexpected error textually
        return f"An unexpected error occurred: {str(e)}"
