# core/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Edital, ServidorProfile, TipoAtividade, Atividade, LancamentoHoras

# Helper function to create users with profiles
def create_user_with_profile(username, password, funcao, first_name="Test", last_name="User"):
    user = User.objects.create_user(username=username, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.servidorprofile.funcao = funcao
    user.servidorprofile.status = 'Homologado'
    user.servidorprofile.save()
    user.save()
    return user

class ModelTests(TestCase):
    
    def setUp(self):
        self.demandante = create_user_with_profile('demandante', 'password', 'Unidade Demandante')
        self.servidor = create_user_with_profile('servidor', 'password', 'Servidor')
        self.prodgep = create_user_with_profile('prodgep', 'password', 'PRODGEP/PROPEG')

        self.tipo_atividade = TipoAtividade.objects.create(
            grupo='Banca', nome='Correção de Prova', valor_hora=50.00
        )

        self.edital = Edital.objects.create(
            criado_por=self.demandante,
            numero_edital='001/2025-TEST',
            titulo='Edital de Teste',
            unidade_demandante_nome='PRODGEP',
            data_inicio=timezone.now().date(),
            data_fim=timezone.now().date()
        )

    def test_servidor_profile_creation(self):
        """Testa se o ServidorProfile é criado automaticamente com o User."""
        self.assertIsNotNone(self.demandante.servidorprofile)
        self.assertEqual(self.demandante.servidorprofile.funcao, 'Unidade Demandante')

    def test_edital_str_representation(self):
        """Testa o método __str__ do Edital."""
        expected_str = f"{self.edital.numero_edital} - {self.edital.titulo}"
        self.assertEqual(str(self.edital), expected_str)

    def test_tipo_atividade_str(self):
        """Testa o método __str__ do TipoAtividade."""
        expected_str = f"Correção de Prova (R$ {self.tipo_atividade.valor_hora:.2f}/h)"
        self.assertEqual(str(self.tipo_atividade), expected_str)


class ViewAccessTests(TestCase):

    def setUp(self):
        self.demandante = create_user_with_profile('demandante', 'password', 'Unidade Demandante')
        self.servidor = create_user_with_profile('servidor', 'password', 'Servidor')
        self.prodgep = create_user_with_profile('prodgep', 'password', 'PRODGEP/PROPEG')

        self.edital = Edital.objects.create(
            criado_por=self.demandante,
            numero_edital='001/2025-TEST',
            titulo='Edital de Teste',
            unidade_demandante_nome='PRODGEP',
            data_inicio=timezone.now().date(),
            data_fim=timezone.now().date()
        )

    def test_listar_editais_access(self):
        """Testa se apenas a Unidade Demandante pode acessar a lista de editais."""
        self.client.login(username='demandante', password='password')
        response = self.client.get(reverse('listar_editais'))
        self.assertEqual(response.status_code, 200) # 200 = OK

        self.client.login(username='servidor', password='password')
        response = self.client.get(reverse('listar_editais'))
        self.assertEqual(response.status_code, 302) # 302 = Redirecionamento

    def test_unidade_demandante_cannot_see_other_users_editais(self):
        """Testa se uma Unidade Demandante não pode ver detalhes do edital de outra."""
        outro_demandante = create_user_with_profile('outro_demandante', 'password', 'Unidade Demandante')
        
        self.client.login(username='outro_demandante', password='password')
        response = self.client.get(reverse('detalhes_edital', args=[self.edital.pk]))
        self.assertEqual(response.status_code, 302) # Deve ser redirecionado
        self.assertRedirects(response, reverse('listar_editais'))

    def test_create_edital_view(self):
        """Testa se a Unidade Demandante pode criar um edital via POST."""
        self.client.login(username='demandante', password='password')
        
        edital_data = {
            'numero_edital': '002/2025-POST',
            'titulo': 'Edital Criado Via Teste',
            'unidade_demandante_nome': 'TESTE',
            'data_inicio': timezone.now().date(),
            'data_fim': timezone.now().date() + timezone.timedelta(days=30),
            'valor_empenho': 1000.00
        }
        
        response = self.client.post(reverse('criar_edital'), data=edital_data)
        
        # Testa se foi redirecionado para a lista após criar
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_editais'))
        
        # Testa se o edital realmente existe no banco de dados
        self.assertTrue(Edital.objects.filter(numero_edital='002/2025-POST').exists())