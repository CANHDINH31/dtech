# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User

class UserList(APIView):
    def get(self, request):
        users = User.objects()
        data = [{"id": str(user.id), "name": user.name, "email": user.email} for user in users]
        return Response(data)

    def post(self, request):
        data = request.data
        user = User(name=data.get('name'), email=data.get('email'))
        user.save()
        return Response({"id": str(user.id)}, status=status.HTTP_201_CREATED)
