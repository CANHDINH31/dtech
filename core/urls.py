from django.urls import path
from .views import QuestionList

urlpatterns = [
    path('questions/', QuestionList.as_view(), name='question'),
]