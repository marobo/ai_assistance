from unittest.mock import patch

from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse

from .core import ask_ai
from .utils import (
    CHAT_SESSION_KEY,
    get_chat_history,
    save_chat_history,
    clear_chat_history,
)


class AskAICoreHistoryTests(TestCase):
    @patch('ai_assistance.core.httpx.post')
    def test_ask_ai_includes_history_in_payload(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'choices': [{'message': {'content': 'ok'}}],
        }

        ask_ai(
            'Follow up?',
            api_key='key',
            system_prompt='sys',
            history=[
                {'role': 'user', 'content': 'Hi'},
                {'role': 'assistant', 'content': 'Hello'},
            ],
        )

        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(
            payload['messages'],
            [
                {'role': 'system', 'content': 'sys'},
                {'role': 'user', 'content': 'Hi'},
                {'role': 'assistant', 'content': 'Hello'},
                {'role': 'user', 'content': 'Follow up?'},
            ],
        )


@override_settings(
    OPENROUTER_API_KEY='test-key',
    AI_ASSISTANCE_BASE_TEMPLATE='ai_assistance/test_base.html',
    AI_ASSISTANCE_BASE_TEMPLATE_FUNC=None,
    STORAGES={
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)
class AskAIChatHistoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('ai_assistance:ask_ai')

    @patch('ai_assistance.views.core_ask_ai')
    def test_post_appends_messages_to_session(self, mock_ask):
        mock_ask.return_value = 'Hello answer'

        response = self.client.post(self.url, {'question': 'Hello?'})

        self.assertEqual(response.status_code, 200)
        history = self.client.session[CHAT_SESSION_KEY]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], {'role': 'user', 'content': 'Hello?'})
        self.assertEqual(
            history[1], {'role': 'assistant', 'content': 'Hello answer'}
        )
        mock_ask.assert_called_once()
        self.assertEqual(mock_ask.call_args.kwargs.get('history'), [])

    @patch('ai_assistance.views.core_ask_ai')
    def test_follow_up_sends_prior_history(self, mock_ask):
        mock_ask.side_effect = ['First answer', 'Second answer']

        self.client.post(self.url, {'question': 'First?'})
        self.client.post(self.url, {'question': 'Second?'})

        self.assertEqual(mock_ask.call_count, 2)
        second_history = mock_ask.call_args_list[1].kwargs.get('history')
        self.assertEqual(
            second_history,
            [
                {'role': 'user', 'content': 'First?'},
                {'role': 'assistant', 'content': 'First answer'},
            ],
        )
        history = self.client.session[CHAT_SESSION_KEY]
        self.assertEqual(len(history), 4)

    @patch('ai_assistance.views.core_ask_ai')
    def test_clear_resets_history(self, mock_ask):
        mock_ask.return_value = 'Answer'
        self.client.post(self.url, {'question': 'Hello?'})

        response = self.client.post(self.url, {'clear': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(CHAT_SESSION_KEY, self.client.session)
        self.assertEqual(response.context['chat_messages'], [])
        self.assertNotContains(response, 'Hello?')
        mock_ask.assert_called_once()

    def test_chat_history_helpers_noop_without_session(self):
        request = RequestFactory().get(self.url)

        self.assertEqual(get_chat_history(request), [])
        save_chat_history(request, [{'role': 'user', 'content': 'Hello?'}])
        clear_chat_history(request)

    @override_settings(
        AI_ASSISTANCE_CHAT_MAX_MESSAGES=20,
        AI_ASSISTANCE_CHAT_MAX_SESSION_BYTES=120,
    )
    def test_save_chat_history_trims_by_serialized_size(self):
        session = self.client.session
        session[CHAT_SESSION_KEY] = []
        session.save()

        request = RequestFactory().get(self.url)
        request.session = self.client.session
        history = [
            {'role': 'user', 'content': 'x' * 80},
            {'role': 'assistant', 'content': 'y' * 80},
            {'role': 'user', 'content': 'short'},
        ]

        save_chat_history(request, history)

        self.assertEqual(
            request.session[CHAT_SESSION_KEY],
            [{'role': 'user', 'content': 'short'}],
        )

    @patch('ai_assistance.views.core_ask_ai')
    def test_chat_messages_rendered_in_template(self, mock_ask):
        mock_ask.return_value = 'Hello answer'

        response = self.client.post(self.url, {'question': 'Hello?'})

        self.assertContains(response, 'Hello?')
        self.assertContains(response, 'Hello answer')
        self.assertEqual(len(response.context['chat_messages']), 2)
