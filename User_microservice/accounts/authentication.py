from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from bson.objectid import ObjectId
from django.conf import settings

class MongoJWTAuthentication(JWTAuthentication):
    user_id_claim = api_settings.USER_ID_CLAIM

    def get_user(self, validated_token):
        try:
            user_id = validated_token[self.user_id_claim]
            user_data = settings.USER_COLLECTION.find_one({"_id": ObjectId(user_id)})
            if not user_data:
                raise AuthenticationFailed("User not found", code="user_not_found")
            
            class MongoUser:
                def __init__(self, data):
                    self.id = str(data["_id"])
                    self.email = data.get("email")
                
                @property
                def is_authenticated(self):
                    return True
            
            return MongoUser(user_data)
        except Exception as e:
            raise AuthenticationFailed(str(e))
