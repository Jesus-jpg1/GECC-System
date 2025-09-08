# core/management/commands/create_test_lancamentos.py

import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Edital, Atividade, User, LancamentoHoras

class Command(BaseCommand):
    help = 'Cria lançamentos de horas de teste, associando servidores e atividades de editais existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--total', type=int, default=15, help='Indica o número de lançamentos de horas a serem criados.')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        
        # Busca por usuários que são servidores e por editais que tenham atividades
        servidores = User.objects.filter(servidorprofile__funcao='Servidor')
        editais_com_atividades = Edital.objects.filter(atividades__isnull=False).distinct()

        if not servidores.exists():
            self.stdout.write(self.style.ERROR('Nenhum usuário com a função "Servidor" encontrado. Crie alguns com o comando "create_test_users".'))
            return
            
        if not editais_com_atividades.exists():
            self.stdout.write(self.style.ERROR('Nenhum edital com atividades associadas encontrado. Crie editais e adicione atividades primeiro.'))
            return

        self.stdout.write(self.style.NOTICE(f'Criando {total} lançamentos de horas de teste...'))
        
        lancamentos_criados = 0
        for _ in range(total):
            # Seleciona aleatoriamente um edital e um servidor
            edital_aleatorio = random.choice(editais_com_atividades)
            servidor_aleatorio = random.choice(servidores)
            
            # Seleciona aleatoriamente uma das atividades daquele edital
            atividade_aleatoria = random.choice(edital_aleatorio.atividades.all())

            # Gera dados aleatórios para o lançamento
            data_aleatoria = timezone.now().date() - timedelta(days=random.randint(1, 30))
            horas_aleatorias = round(random.uniform(1.0, 8.0), 2)
            
            LancamentoHoras.objects.create(
                servidor=servidor_aleatorio,
                edital=edital_aleatorio,
                atividade=atividade_aleatoria,
                data=data_aleatoria,
                horas=horas_aleatorias,
                descricao_justificativa=f'Execução da atividade {atividade_aleatoria.tipo.nome} conforme o planejado.',
                status='Pendente' # Todos os lançamentos são criados como pendentes
            )
            lancamentos_criados += 1

        self.stdout.write(self.style.SUCCESS(f'{lancamentos_criados} lançamentos de horas criados com sucesso!'))