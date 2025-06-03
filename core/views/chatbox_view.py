# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import ResearchDocument
from ..serializers import ResearchDocumentSerializer
import requests
from ..utils.text_utils import clean_text
from django.conf import settings


# GEMINI_API_KEY = "AIzaSyACeMStY69pEIBlrXD9yN-TDbH7YH9Ro5Q"
# OPENAI_API_KEY = "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"

class ChatBoxView(APIView):
    def post(self, request):
        data = request.data

        question = data.get("question")
        model_name = data.get("model", "gemini").lower()

        if not question or not isinstance(question, str):
            return Response({"error": "Missing or invalid 'question' field"}, status=status.HTTP_400_BAD_REQUEST)

        if model_name == "gemini":
            answer = self._ask_gemini(question)
        elif model_name == "openai":
            answer = self._ask_openai(question)
        else:
            return Response({"error": f"Model '{model_name}' not supported"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"answer": answer})
    
    
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

