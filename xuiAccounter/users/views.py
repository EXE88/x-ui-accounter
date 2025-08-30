from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserMetaDataSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from coins.models import Coin
import re

class UserRegister(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password:
            return Response({"error": "please send all required fields"}, status=400)

        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long."}, status=400)
        if len(password) > 128:
            return Response({"error": "Password must be at most 128 characters long."}, status=400)

        if len(username) < 8:
            return Response({"error": "username must be at least 8 characters long."}, status=400)
        if len(username) > 128:
            return Response({"error": "username must be at most 128 characters long."}, status=400)

        if not re.match(r'^[\w.@+-]+$', username):
            return Response({"error": "username contains invalid characters."}, status=403)

        if User.objects.filter(username=username).exists():
            return Response({"error": "A user with this username already exists."}, status=409)

        new_user = User(username=username)
        new_user.set_password(password)
        new_user.save()

        if email:
            metadata_serializer = UserMetaDataSerializer(data={"email": email})
            if metadata_serializer.is_valid():
                try:
                    metadata_serializer.save(user=new_user)
                    init_coins = Coin.objects.create(user=new_user,number_of_coins=0)
                    init_coins.save()
                    return Response({"info": "account created successfully."}, status=201)
                except Exception as e:
                    new_user.delete()
                    return Response({"error": f"Error saving user metadata: {str(e)}"}, status=500)
            else:
                new_user.delete()
                return Response({"error": metadata_serializer.errors}, status=400)
        else:
            new_user.delete()
            return Response({"error": "please send all required fields"}, status=400)