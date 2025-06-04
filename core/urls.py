from django.urls import path
from .views import QAView,TrainView,DocView,PlagiarismCheckView,ChatBoxView,UploadView

urlpatterns = [
    path('questions/', QAView.as_view(), name='question'),
    path('chatbox/', ChatBoxView.as_view(), name='chatbox'),
    path('docs/', DocView.as_view(), name="doc"),
    path('docs/<str:doc_id>/', DocView.as_view(), name="doc-detail"),
    path('train/', TrainView.as_view(), name='train'),
    path("check-plagiarism/", PlagiarismCheckView.as_view(), name="check_plagiarism"),
    path('upload/', UploadView.as_view(), name='upload'),
]