from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Edital(models.Model):
    STATUS_CHOICES = [
        ('Em Elaboração', 'Em Elaboração'),
        ('Aguardando Homologação', 'Aguardando Homologação'),
        ('Homologado', 'Homologado'),
        ('Recusado', 'Recusado'),
    ]

    titulo = models.CharField(max_length=255)
    numero_edital = models.CharField(max_length=50, unique=True)
    unidade_demandante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='editais_criados')
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Em Elaboração')
    valor_empenho = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.numero_edital} - {self.titulo}"

class ServidorProfile(models.Model):
    TIPO_VINCULO_CHOICES = [
        ('UFAC', 'UFAC'),
        ('Externo', 'Externo'),
    ]
    FUNCAO_CHOICES = [
        ('Unidade Demandante', 'Unidade Demandante'),
        ('Servidor', 'Servidor'),
        ('PRODGEP/PROPEG', 'PRODGEP/PROPEG'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, unique=True) # Ex: 123.456.789-00
    tipo_vinculo = models.CharField(max_length=10, choices=TIPO_VINCULO_CHOICES)
    funcao = models.CharField(max_length=20, choices=FUNCAO_CHOICES)

    def __str__(self):
        return self.user.username

# Este signal (sinal) cria um ServidorProfile automaticamente sempre que um novo User é criado.
# É uma forma de manter os dois modelos sincronizados.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ServidorProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.servidorprofile.save()


class Atividade(models.Model):
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='atividades')
    descricao = models.TextField()
    servidores_alocados = models.ManyToManyField(User, related_name='atividades_alocadas')

    def __str__(self):
        return f"Atividade do Edital {self.edital.numero_edital}: {self.descricao[:50]}..."

class LancamentoHoras(models.Model):
    STATUS_CHOICES = [
        ('Lançado', 'Lançado'),
        ('Aprovado', 'Aprovado'),
        ('Recusado', 'Recusado'),
    ]

    servidor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='lancamentos')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='lancamentos')
    data = models.DateField()
    horas_trabalhadas = models.DecimalField(max_digits=4, decimal_places=2)
    justificativa = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Lançado')

    def __str__(self):
        return f"Lançamento de {self.servidor.username} em {self.data}"