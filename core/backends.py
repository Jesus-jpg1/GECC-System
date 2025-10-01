# core/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class ProfileStatusBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1. Deixa o Django fazer a validação de usuário e senha primeiro.
        # Se estiverem errados, o Django já retorna None (nulo).
        user = super().authenticate(request, username=username, password=password, **kwargs)

        # Se o login/senha falhou, não fazemos mais nada.
        if user is None:
            return None

        # 2. Se a senha está correta, fazemos nossa checagem extra.
        # A regra é: permita o login se o usuário for um superusuário OU se o status do seu perfil for 'Homologado'.
        if user.is_superuser or (hasattr(user, 'servidorprofile') and user.servidorprofile.status == 'Homologado'):
            return user
        
        # 3. Se a checagem extra falhar (ex: status 'Recusado'), negamos o login.
        return None

    def get_user(self, user_id):
        # Esta função é necessária para o sistema de sessão do Django.
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None