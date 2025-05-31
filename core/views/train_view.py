from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Question
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class TrainView(APIView):
    def post(self, request):
        questions = Question.objects()
        updated = 0
        for q in questions:
            try:
                emb = model.encode(q.question).tolist()
                q.embedding = emb
                q.save()
                updated += 1
            except Exception as e:
                continue

        return Response({
            "message": "Train completed",
            "total_trained": updated
        }, status=status.HTTP_200_OK)