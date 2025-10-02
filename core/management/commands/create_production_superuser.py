# core/management/commands/create_production_superuser.py

import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Cria um superusuário para o ambiente de produção de forma não-interativa.'

    def handle(self, *args, **kwargs):
        username = os.environ.get('PROD_SUPERUSER_USERNAME')
        email = os.environ.get('PROD_SUPERUSER_EMAIL')
        password = os.environ.get('PROD_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            raise CommandError('As variáveis de ambiente PROD_SUPERUSER_USERNAME, PROD_SUPERUSER_EMAIL e PROD_SUPERUSER_PASSWORD devem ser definidas.')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" já existe. Nenhum foi criado.'))
            return

        self.stdout.write(self.style.NOTICE(f'Criando superusuário de produção: {username}'))
        
        User.objects.create_superuser(username=username, email=email, password=password)
        
        self.stdout.write(self.style.SUCCESS(f'Superusuário "{username}" criado com sucesso!'))