from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Question
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

model = SentenceTransformer('all-MiniLM-L6-v2')

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
                "correct_answer": q.correct_answer,
                "has_embedding": bool(q.embedding)
            })
        return Response(data)
    
    def post(self, request):
        # Nếu dữ liệu gửi lên là 1 câu hỏi dạng string, tìm câu hỏi gần nhất và trả lời
        if isinstance(request.data, dict) and 'question' in request.data and isinstance(request.data['question'], str):
            user_question = request.data['question']
            user_emb = model.encode(user_question)
            
            questions = Question.objects(__raw__={
                '$and': [
                    {'embedding': {'$exists': True}},
                    {'embedding': {'$ne': []}}
                ]
            })

            thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] # thresholds càng bé thì chuẩn xác cao nhưng ít câu hỏi khớp.
            matched_questions = []
            used_threshold = None

            for threshold in thresholds:
                matched_questions = []
                for q in questions:
                    dist = cosine(user_emb, q.embedding)
                    if dist < threshold:
                        matched_questions.append({
                            "id": str(q.id),
                            "question": q.question,
                            "a": q.a,
                            "b": q.b,
                            "c": q.c,
                            "d": q.d,
                            "correct_answer": q.correct_answer,
                            "similarity_score": 1 - dist
                        })
                if matched_questions:
                    used_threshold = threshold
                    break

            matched_questions = sorted(matched_questions, key=lambda x: x['similarity_score'], reverse=True)

            if matched_questions:
                return Response({
                    "matched_questions": matched_questions,
                    "used_threshold": used_threshold
                })
            else:
                return Response({
                    "message": "No matching question found",
                    "used_threshold": thresholds[-1]
                }, status=404)

        # Nếu gửi lên là list câu hỏi mới thì tạo mới như trước
        elif isinstance(request.data, list):
            questions_data = request.data
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

        else:
            return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
