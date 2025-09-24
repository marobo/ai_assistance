# AI Assistance Django App

A Django application that provides AI-powered assistance through integration with Anthropic's Claude API. This app allows users to ask questions and receive intelligent responses from Claude AI within a Django web application.

## Features

- **AI Question Interface**: Clean, user-friendly form for submitting questions to AI
- **Claude API Integration**: Powered by Anthropic's Claude-3-Opus model
- **Internationalization Support**: Built-in support for multiple languages using Django's i18n framework
- **HTMX Integration**: Dynamic form submission without page reloads
- **Error Handling**: Comprehensive error handling for API failures, timeouts, and authentication issues
- **Bootstrap UI**: Modern, responsive user interface using Bootstrap components

## Installation

### As a Git Submodule

This app is designed to be used as a git submodule in your main Django project:

```bash
# Add as submodule
git submodule add git@github.com:marobo/ai_assistance.git ai_assistance

# Initialize and update submodule
git submodule update --init --recursive
```

### Django Integration

1. **Add to INSTALLED_APPS** in your Django settings:
```python
INSTALLED_APPS = [
    # ... your other apps
    'ai_assistance',
]
```

2. **Configure API Key** in your settings:
```python
# Required: Anthropic API key
ANTHROPIC_API_KEY = 'your-anthropic-api-key-here'
```

3. **Include URLs** in your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... your other URLs
    path('', include('ai_assistance.urls')),
]
```

4. **Run migrations** (if any are added in the future):
```bash
python manage.py migrate
```

## Dependencies

This app requires the following Python packages:

- `Django` (compatible with Django's internationalization framework)
- `httpx` (for HTTP requests to Anthropic API)

Add to your `requirements.txt`:
```
httpx>=0.24.0
```

## Configuration

### Required Settings

- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude access

### Optional Settings

The app uses Django's built-in internationalization framework, so you can configure:
- `LANGUAGE_CODE`: Default language
- `USE_I18N`: Enable internationalization (should be `True`)
- `LOCALE_PATHS`: For custom translations

## Usage

### Accessing the AI Assistant

Once installed and configured, users can access the AI assistant at:
```
http://localhost:8000/ask-ai/
```

### Features Available

1. **Ask Questions**: Users can submit any question through a textarea form
2. **Get AI Responses**: Receive intelligent responses from Claude AI
3. **Error Handling**: Graceful handling of API errors with user-friendly messages

### API Integration Details

- **Model**: Claude-3-Opus (claude-3-opus-20240229)
- **Max Tokens**: 300 per response
- **Timeout**: 20 seconds
- **API Version**: 2023-06-01

## File Structure

```
ai_assistance/
├── __init__.py
├── apps.py                 # Django app configuration
├── admin.py               # Django admin configuration
├── models.py              # Database models (currently empty)
├── views.py               # Main view logic and Claude API integration
├── urls.py                # URL routing
├── tests.py               # Unit tests
├── migrations/            # Database migrations
├── templates/
│   └── ai_assistance/
│       ├── ai_question_page.html    # Question form interface
│       └── ai_response.html         # Response display page
├── LICENSE                # MIT License
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## Error Handling

The app includes comprehensive error handling for:

- **Missing API Key**: Displays configuration error message
- **Authentication Failures**: API key validation errors
- **Rate Limiting**: Handles API rate limit responses
- **Network Timeouts**: Connection timeout handling
- **General API Errors**: Graceful handling of other API issues

## Security Considerations

- API keys should be stored securely (use environment variables)
- The app includes CSRF protection for form submissions
- Input validation prevents empty question submissions

## Contributing

This is a git submodule, so contributions should be made to the original repository. When making changes:

1. Make changes in the submodule directory
2. Commit changes in the submodule
3. Update the parent project to reference the new commit

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues related to:
- **Django Integration**: Check Django documentation and ensure proper configuration
- **API Issues**: Verify your Anthropic API key and account status
- **UI Problems**: Ensure Bootstrap and HTMX are properly loaded in your base template

## Version Compatibility

- **Django**: 3.2+ (uses modern class-based views and i18n)
- **Python**: 3.8+ (required for httpx)
- **Anthropic API**: Uses 2023-06-01 API version
