from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.permissions import IsAuthenticated
from bson.objectid import ObjectId

from .serializers import UserLoginSerializer, UserRegisterSerializer, UserDetailSerializer

class UserRegisterView(APIView):
    serializer_class = UserRegisterSerializer
    
    def post(self, request):
        ser_data = self.serializer_class(data=request.data)
        ser_data.is_valid(raise_exception=True)
        vd = ser_data.validated_data
        vd["password"] = make_password(vd["password"])
        result = settings.USER_COLLECTION.insert_one(vd)
        return Response(data={"message":ser_data.data, "user_id":str(result.inserted_id)}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        ser_data = self.serializer_class(data=request.data)
        ser_data.is_valid(raise_exception=True)
        print(ser_data.validated_data)
        vd = ser_data.validated_data
        user = settings.USER_COLLECTION.find_one({"email": vd["email"]})
        if user and check_password(vd["password"], user["password"]):
            refresh_token = RefreshToken()
            access_token = AccessToken()
            
            refresh_token['user_id'], access_token['user_id'] = str(user['_id']), str(user['_id'])

            return Response(data={
                'refresh_token': str(refresh_token),
                'access_token': str(access_token)
            }, status=status.HTTP_200_OK)
        return Response(data={"Error": "we Can Not find user or password is wrong"},
                        status=status.HTTP_401_UNAUTHORIZED)
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializr_class = UserDetailSerializer
    
    def get(self, request, user_id):
        user = settings.USER_COLLECTION.find_one({"_id": ObjectId(user_id)})

        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user["_id"] = str(user["_id"])
        user.pop("password", None)

        return Response(data=user, status=status.HTTP_200_OK)
    

class AuthMicroserviceView(APIView):

    def get(self, request):
        print("BB")
        user_id = request.user.id
        print(user_id)
        user_data = settings.USER_COLLECTION.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data.pop("password", None)
            user_data['_id'] = str(user_data.get('_id', None))
            user_info = user_data
            return Response(data=user_info, status=status.HTTP_200_OK)
        return Response(data={"message": "something is wrong."}
                        ,status=status.HTTP_400_BAD_REQUEST)
