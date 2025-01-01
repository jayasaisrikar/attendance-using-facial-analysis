from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            print(f"Attempting to authenticate email: {email}")
            user = UserModel.objects.get(email=email)
            print(f"Found user: {user.email}")
            
            if user.check_password(password):
                print(f"Password check passed for user: {user.email}")
                return user
            print("Password check failed")
            return None
        except UserModel.DoesNotExist:
            print(f"No user found with email: {email}")
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None 
            return None 