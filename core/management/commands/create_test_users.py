# core/management/commands/create_test_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ServidorProfile

class Command(BaseCommand):
    help = 'Cria uma quantidade especificada de usuários de teste com o perfil de Servidor.'

    def add_arguments(self, parser):
        # Argumento opcional para definir quantos usuários criar
        parser.add_argument('total', type=int, nargs='?', default=5, help='Indica o número de usuários a serem criados.')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        
        self.stdout.write(self.style.NOTICE(f'Criando {total} usuários de teste com perfil de Servidor...'))

        for i in range(total):
            username = f'servidor_teste_{i+1}'
            password = 'password123'
            
            # Evita erro se o usuário já existir
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Usuário {username} já existe. Pulando.'))
                continue

            # Cria o usuário
            user = User.objects.create_user(username=username, password=password)
            
            # Define o nome e sobrenome
            user.first_name = f'Servidor'
            user.last_name = f'Teste {i+1}'
            user.save()
            
            # Acessa o perfil criado automaticamente pelo 'signal' e define a função
            user.servidorprofile.funcao = 'Servidor'
            user.servidorprofile.siape = f'12345{i+1}'
            user.servidorprofile.cpf = f'111.222.333-{i+1:02d}' 
            user.servidorprofile.save()

            self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado com sucesso.'))
            
        self.stdout.write(self.style.SUCCESS('Operação concluída!'))