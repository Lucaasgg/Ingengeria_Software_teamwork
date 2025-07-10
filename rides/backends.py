from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Authenticate using email instead of username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Here 'username' will actually be the email from the form
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
