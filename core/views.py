# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Question

class QuestionList(APIView):
    def post(self, request):
        data = request.data
        try:
            question = Question(
                question=data.get("question"),
                a=data.get("a"),
                b=data.get("b"),
                c=data.get("c"),
                d=data.get("d"),
                correct_answer=data.get("correct_answer"),
            )
            question.save()
            return Response({"id": str(question.id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
