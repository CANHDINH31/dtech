# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Question

class QAView(APIView):
    def get(self, request):
        questions = Question.objects()  
        data = []
        for q in questions:
            data.append({
                "id": str(q.id),
                "question": q.question,
                "a": q.a,
                "b": q.b,
                "c": q.c,
                "d": q.d,
                "correct_answer": q.correct_answer
            })
        return Response(data)
    
    def post(self, request):
        questions_data = request.data
        if not isinstance(questions_data, list):
            return Response({"error": "Expected a list of questions"}, status=status.HTTP_400_BAD_REQUEST)

        created_ids = []
        errors = []

        for idx, data in enumerate(questions_data):
            try:
                q = Question(
                    question=data.get('question'),
                    a=data.get('a'),
                    b=data.get('b'),
                    c=data.get('c'),
                    d=data.get('d'),
                    correct_answer=data.get('correct_answer')
                )
                q.save()
                created_ids.append(str(q.id))
            except Exception as e:
                errors.append({"index": idx, "error": str(e)})

        return Response({
            "created_ids": created_ids,
            "errors": errors
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)

