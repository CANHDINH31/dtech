# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.search_full_text_core import PlagiarismChecker

checker = PlagiarismChecker()
class PlagiarismCheckView(APIView):
    def post(self, request):
            query = request.data.get("text")
            if not query:
                return Response({"error": "Missing 'text' field"}, status=status.HTTP_400_BAD_REQUEST)
            
            results = checker.check(query)
            return Response({"results": results}, status=status.HTTP_200_OK)