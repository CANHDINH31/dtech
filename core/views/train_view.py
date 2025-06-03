from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Question
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class TrainView(APIView):
    def post(self, request):
        questions = Question.objects(__raw__={
            '$or': [
                {'embedding': {'$exists': False}},
                {'embedding': {'$size': 0}}
            ]
        })
        updated = 0
        for q in questions:
            try:
                full_text = f"{q.question} {q.a} {q.b} {q.c} {q.d}"
                emb = model.encode(full_text).tolist()
                q.embedding = emb
                q.save()
                updated += 1
            except Exception as e:
                continue

        return Response({
            "message": "Train completed",
            "total_trained": updated
        }, status=status.HTTP_200_OK)