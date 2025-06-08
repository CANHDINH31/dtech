# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import ResearchDocument
from ..serializers import ResearchDocumentSerializer
import requests
from ..utils.text_utils import clean_text
from django.conf import settings
from openai import OpenAI


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
    
    def _ask_openai(self, prompt: str) -> str:
        try:
            client = OpenAI(
                api_key= settings.OPENAI_API_KEY,
            )

            response = client.responses.create(
                model="gpt-4o",
                input=prompt,
            )
            
            return Response({"answer": response.output_text})

        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"

