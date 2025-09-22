# core/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class ProfileStatusBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta encontrar o usuário pelo username.
            user = User.objects.get(username=username)
            
            # Verifica se a senha está correta E se o perfil está homologado.
            if user.check_password(password) and user.servidorprofile.status == 'Homologado':
                # Se tudo estiver certo, permite o login.
                return user
        except User.DoesNotExist:
            # Se o usuário não existe, falha a autenticação.
            return None
        except AttributeError:
            # Se o usuário não tem perfil (ex: superusuário antigo), nega o login.
            return None
        
        # Se a senha estiver errada ou o status não for 'Homologado', nega o login.
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None