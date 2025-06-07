from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Question
from ..utils.text_utils import extract_keywords, clean_text
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
import requests
from django.conf import settings


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
        if self._is_single_question(request.data):
            return self._handle_single_question(request.data['question'])

        elif isinstance(request.data, list):
            return self._handle_bulk_create(request.data)

        return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
        
    def _is_single_question(self, data):
        return isinstance(data, dict) and 'question' in data and isinstance(data['question'], str)
    
    def _handle_single_question(self, user_question: str):
        print(user_question, "user_question")
        user_emb = model.encode(user_question)
        keywords = extract_keywords(user_question)
        questions = self._get_trained_questions()

        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
        matched_questions, used_threshold = self._search_by_thresholds(user_emb, questions, keywords, thresholds)

        if matched_questions:
            return Response({
                "matched_questions": matched_questions,
                "used_threshold": used_threshold
            })
        else:
            gemini_response = self._ask_gemini(user_question)
            return Response({
                "message": "No matching question found",
                "used_threshold": thresholds[-1],
                "gemini_response": gemini_response
            })

    def _get_trained_questions(self):
        return Question.objects(__raw__={
            '$and': [
                {'embedding': {'$exists': True}},
                {'embedding': {'$ne': []}}
            ]
        })
        
    def _search_by_thresholds(self, user_emb, questions, keywords, thresholds):
        for threshold in thresholds:
            matched = []
            for q in questions:
                dist = cosine(user_emb, q.embedding)
                if dist < threshold and any(k.lower() in q.question.lower() for k in keywords):
                    matched.append({
                        "id": str(q.id),
                        "question": q.question,
                        "a": q.a,
                        "b": q.b,
                        "c": q.c,
                        "d": q.d,
                        "correct_answer": q.correct_answer,
                        "similarity_score": 1 - dist
                    })
            if matched:
                matched_sorted = sorted(matched, key=lambda x: x['similarity_score'], reverse=True)
                return matched_sorted, threshold
        return [], None

    def _handle_bulk_create(self, questions_data):
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
    
    def _ask_gemini(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
            return clean_text(raw_text)
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

