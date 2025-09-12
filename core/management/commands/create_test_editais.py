# core/management/commands/create_test_editais.py

import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import Edital


class Command(BaseCommand):
    help = "Cria editais de teste para um usuário Unidade Demandante existente."

    def add_arguments(self, parser):
        # Argumento obrigatório com o username
        parser.add_argument(
            "username",
            type=str,
            help="O nome de usuário da Unidade Demandante que será a criadora dos editais.",
        )

        # Argumento opcional para a quantidade
        parser.add_argument(
            "--total",
            type=int,
            default=5,
            help="Indica o número de editais a serem criados.",
        )

    def handle(self, *args, **kwargs):
        username = kwargs["username"]
        total = kwargs["total"]

        try:
            user = User.objects.get(username=username)
            if user.servidorprofile.funcao != "Unidade Demandante":
                raise CommandError(
                    f'O usuário "{username}" não tem a função de Unidade Demandante.'
                )
        except User.DoesNotExist:
            raise CommandError(f'Usuário "{username}" não encontrado.')

        self.stdout.write(
            self.style.NOTICE(
                f'Criando {total} editais de teste para o usuário "{username}"...'
            )
        )

        status_choices = [status[0] for status in Edital.STATUS_CHOICES]

        for i in range(total):
            # Gera um número de edital único
            numero = f"{i + 1:03d}/{timezone.now().year}-TESTE"

            # Garante que não haja duplicatas
            if Edital.objects.filter(numero_edital=numero).exists():
                continue

            Edital.objects.create(
                criado_por=user,
                numero_edital=numero,
                titulo=f'Edital de Teste {i + 1} para a Área de {random.choice(["Saúde", "Tecnologia", "Humanas", "Exatas"])}',
                descricao="Descrição padrão para o edital de teste.",
                unidade_demandante_nome=user.servidorprofile.setor or "Unidade Teste",
                data_inicio=timezone.now().date(),
                data_fim=timezone.now().date() + timedelta(days=30),
                status=random.choice(status_choices),
                valor_empenho=random.uniform(5000.00, 50000.00),
            )
            self.stdout.write(self.style.SUCCESS(f'Edital "{numero}" criado.'))

        self.stdout.write(self.style.SUCCESS("Operação concluída!"))
