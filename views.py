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
)


class AskAIView(View):
    def get(self, request):
        base_template = resolve_base_template(request)
        return render(request, 'ai_assistance/ai_question_page.html', {
            'base_template': base_template,
            'ai_hx_target_id': resolve_hx_target_id(),
            'intro_text': resolve_intro_text(request),
        })

    def post(self, request):
        base_template = resolve_base_template(request)
        question = request.POST.get('question', '').strip()

        # Validate that a question was provided
        if not question:
            return render(
                request,
                'ai_assistance/ai_response.html',
                {
                    'response': _(
                        "Please provide a question to get an AI response."
                    ),
                    'question': "",
                    'base_template': base_template,
                    'ai_hx_target_id': resolve_hx_target_id(),
                },
            )

        claude_response = core_ask_ai(
            question,
            api_key=getattr(settings, 'ANTHROPIC_API_KEY', None),
            system_prompt=resolve_system_prompt(request),
            model=resolve_model_name(),
            timeout_seconds=resolve_timeout_seconds(),
        )

        return render(
            request,
            'ai_assistance/ai_response.html',
            {
                'response': claude_response,
                'question': question,
                'base_template': base_template,
                'ai_hx_target_id': resolve_hx_target_id(),
            },
        )


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
            api_key=getattr(settings, 'ANTHROPIC_API_KEY', None),
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
            api_key=getattr(settings, 'ANTHROPIC_API_KEY', None),
            system_prompt=resolve_system_prompt(request),
            model=resolve_model_name(),
            timeout_seconds=resolve_timeout_seconds(),
        )
        return JsonResponse({"answer": answer})
