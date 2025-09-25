import httpx
from typing import Optional


DEFAULT_MODEL = "claude-3-opus-20240229"


def ask_ai(
    prompt: str,
    *,
    api_key: Optional[str],
    system_prompt: str,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = 20,
) -> str:
    """Call the Anthropic API with the given parameters and return the text.

    This function is framework-agnostic and contains no Django imports.
    All configuration must be passed in explicitly by the caller.
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
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    json_data = {
        "model": model,
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=json_data,
            timeout=timeout_seconds,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("content", [{}])[0].get(
                "text",
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
        return (
            f"AI service error (Status: {response.status_code}). "
            "Please try again later."
        )

    except httpx.TimeoutException:
        return "AI service request timed out. Please try again."
    except httpx.RequestError as e:
        return f"AI service connection error: {str(e)}"
    except Exception as e:  # noqa: BLE001 - surface unexpected error textually
        return f"An unexpected error occurred: {str(e)}"
