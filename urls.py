from django.urls import path
from . import views

app_name = 'ai_assistance'

urlpatterns = [
    path('ask-ai/', views.AskAIView.as_view(), name='ask_ai'),
    path('api/ask/', views.AskAIAPIView.as_view(), name='ask_ai_api'),
]
