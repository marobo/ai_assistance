from django.shortcuts import render
from django.conf import settings
import httpx
from django.utils.translation import gettext_lazy as _
from django.views import View
from materiais.views import BaseTemplateSelector


class AskAIView(View):
    def get(self, request):
        base_template = BaseTemplateSelector.get_base_template(request)
        return render(request, 'ai_assistance/ai_question_page.html', {
            'base_template': base_template,
        })

    def post(self, request):
        base_template = BaseTemplateSelector.get_base_template(request)
        question = request.POST.get('question', '').strip()

        # Validate that a question was provided
        if not question:
            return render(request, 'ai_assistance/ai_response.html', {
                'response': _("Please provide a question to get an AI response."),
                'question': "",
                'base_template': base_template,
            })

        claude_response = query_claude(question)

        return render(request, 'ai_assistance/ai_response.html', {
            'response': claude_response,
            'question': question,
            'base_template': base_template,
        })


def query_claude(prompt):
    api_key = settings.ANTHROPIC_API_KEY

    # Check if API key is configured
    if not api_key:
        return _("AI service is currently unavailable. Please contact the administrator to configure the API key.")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    json_data = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=json_data,
            timeout=20
        )

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("content", [{}])[0].get("text", "No reply received from AI.")
        elif response.status_code == 401:
            return _("AI service authentication failed. Please check the API key configuration.")
        elif response.status_code == 429:
            return _("AI service is currently busy. Please try again in a few moments.")
        else:
            return f"{_('AI service error (Status: {response.status_code}). Please try again later.')}"

    except httpx.TimeoutException:
        return _("AI service request timed out. Please try again.")
    except httpx.RequestError as e:
        return _("AI service connection error: {}").format(str(e))
    except Exception as e:
        return _("An unexpected error occurred: {}").format(str(e))