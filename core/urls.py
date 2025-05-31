from django.urls import path
from .views import QAView,TrainView

urlpatterns = [
    path('questions/', QAView.as_view(), name='question'),
    path('train/', TrainView.as_view(), name='train'),
]