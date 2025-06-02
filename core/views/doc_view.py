# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import ResearchDocument
from ..serializers import ResearchDocumentSerializer

class DocView(APIView):
    def get(self, request, doc_id=None):
        if doc_id:
            try:
                doc = ResearchDocument.objects.get(id=doc_id)
                data = {
                    "id": str(doc.id),
                    "author": doc.author,
                    "title": doc.title,
                    "content": doc.content,
                    "year": doc.year,
                }
                return Response(data, status=status.HTTP_200_OK)
            except ResearchDocument.DoesNotExist:
                return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            docs = ResearchDocument.objects()
            data = []
            for d in docs:
                data.append({
                    "id": str(d.id),
                    "author": d.author,
                    "title": d.title,
                    "content": d.content,
                    "year": d.year,
                })
            return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        doc_data = request.data
        if not isinstance(doc_data, list):
            return Response({"error": "Expected a list of questions"}, status=status.HTTP_400_BAD_REQUEST)

        created_ids = []
        errors = []

        for idx, data in enumerate(doc_data):
            try:
                d = ResearchDocument(
                    author=data.get('author'),
                    title=data.get('title'),
                    content=data.get('content'),
                    year=data.get('year'),
                )
                d.save()
                created_ids.append(str(d.id))
            except Exception as e:
                errors.append({"index": idx, "error": str(e)})

        return Response({
            "created_ids": created_ids,
            "errors": errors
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)
    
    def put(self, request, doc_id=None):
        print(doc_id)
        if not doc_id:
            return Response({"error": "Missing document ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = ResearchDocument.objects.get(id=doc_id)
        except ResearchDocument.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResearchDocumentSerializer(data=request.data)
        if serializer.is_valid():
            for attr, value in serializer.validated_data.items():
                setattr(doc, attr, value)
            doc.save()
            return Response({"message": "Updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
    def delete(self, request, doc_id=None):
        if not doc_id:
            return Response({"error": "Missing document ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = ResearchDocument.objects.get(id=doc_id)
            doc.delete()
            return Response({"message": "Deleted successfully"})
        except ResearchDocument.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

