from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views import View

from .core import ask_ai as core_ask_ai
from .rate_limit import is_rate_limited
from .utils import (
    resolve_base_template,
    resolve_system_prompt,
    resolve_model_name,
    resolve_timeout_seconds,
    resolve_hx_target_id,
    resolve_intro_text,
    get_chat_history,
    save_chat_history,
    clear_chat_history,
)


def _rate_limited_response(as_json=False):
    message = _('Too many requests. Please wait and try again.')
    if as_json:
        return JsonResponse({'error': str(message)}, status=429)
    return HttpResponse(str(message), status=429)


class AskAIView(LoginRequiredMixin, View):
    def _render_chat(self, request):
        base_template = resolve_base_template(request)
        return render(request, 'ai_assistance/ai_chat.html', {
            'base_template': base_template,
            'ai_hx_target_id': resolve_hx_target_id(),
            'intro_text': resolve_intro_text(request),
            'chat_messages': get_chat_history(request),
        })

    def get(self, request):
        return self._render_chat(request)

    def post(self, request):
        if request.POST.get('clear'):
            clear_chat_history(request)
            return self._render_chat(request)

        question = request.POST.get('question', '').strip()
        history = get_chat_history(request)

        if not question:
            return self._render_chat(request)

        if is_rate_limited(request):
            return _rate_limited_response(as_json=False)

        ai_response = core_ask_ai(
            question,
            api_key=getattr(settings, 'OPENROUTER_API_KEY', None),
            system_prompt=resolve_system_prompt(request),
            model=resolve_model_name(),
            timeout_seconds=resolve_timeout_seconds(),
            history=list(history),
        )

        history.append({'role': 'user', 'content': question})
        history.append({'role': 'assistant', 'content': ai_response})
        save_chat_history(request, history)

        return self._render_chat(request)


class AskAIAPIView(LoginRequiredMixin, View):
    """Authenticated JSON API for AI answers. POST only."""

    http_method_names = ['post', 'options']

    def post(self, request):
        if is_rate_limited(request):
            return _rate_limited_response(as_json=True)

        question = (
            request.POST.get('question', '').strip()
            or (request.body and self._json_question(request))
            or ''
        )
        if not question:
            return JsonResponse(
                {'error': str(_('Please provide a question.'))}, status=400
            )

        answer = core_ask_ai(
            question,
            api_key=getattr(settings, 'OPENROUTER_API_KEY', None),
            system_prompt=resolve_system_prompt(request),
            model=resolve_model_name(),
            timeout_seconds=resolve_timeout_seconds(),
        )
        return JsonResponse({'answer': answer})

    @staticmethod
    def _json_question(request):
        import json
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ''
        return str(payload.get('question', '')).strip()
