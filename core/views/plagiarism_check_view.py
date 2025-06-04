# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..utils.search_full_text_core import PlagiarismChecker
from threading import Lock

_checker_instance = None
_checker_lock = Lock()

def get_plagiarism_checker():
    global _checker_instance
    if _checker_instance is None:
        with _checker_lock:
            if _checker_instance is None:  
                _checker_instance = PlagiarismChecker()
    return _checker_instance
class PlagiarismCheckView(APIView):
    def post(self, request):
            query = request.data.get("text")
            if not query:
                return Response({"error": "Missing 'text' field"}, status=status.HTTP_400_BAD_REQUEST)
            
            checker = get_plagiarism_checker()
            results = checker.check(query)
            return Response({"results": results}, status=status.HTTP_200_OK)