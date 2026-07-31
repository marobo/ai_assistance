from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import View

from .core import ask_ai as core_ask_ai
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


class AskAIView(View):
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


# For programmatic access via API
class AskAIAPIView(View):
    def get(self, request):
        question = request.GET.get('question', '').strip()
        if not question:
            return JsonResponse(
                {"error": _("Please provide a question.")}, status=400
            )

        answer = core_ask_ai(
            question,
            api_key=getattr(settings, 'OPENROUTER_API_KEY', None),
            system_prompt=resolve_system_prompt(request),
            model=resolve_model_name(),
            timeout_seconds=resolve_timeout_seconds(),
        )
        return JsonResponse({"answer": answer})

    def post(self, request):
        question = (
            request.POST.get('question', '').strip()
            or request.GET.get('question', '').strip()
        )
        if not question:
            return JsonResponse(
                {"error": _("Please provide a question.")}, status=400
            )

        answer = core_ask_ai(
            question,
            api_key=getattr(settings, 'OPENROUTER_API_KEY', None),
            system_prompt=resolve_system_prompt(request),
            model=resolve_model_name(),
            timeout_seconds=resolve_timeout_seconds(),
        )
        return JsonResponse({"answer": answer})
