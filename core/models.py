# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

# O ServidorProfile agora é nosso "super-usuário", com todos os campos extras.
class ServidorProfile(models.Model):
    FUNCAO_CHOICES = [
        ('Unidade Demandante', 'Unidade Demandante'),
        ('PRODGEP/PROPEG', 'PRODGEP/PROPEG'),
        ('Servidor', 'Servidor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campos que pegamos do modelo avançado
    siape = models.CharField(max_length=20, unique=True, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    setor = models.CharField(max_length=100, blank=True)
    funcao = models.CharField(max_length=30, choices=FUNCAO_CHOICES, default='Servidor')
    telefone = models.CharField(max_length=20, blank=True)
    
    # Controle de horas (ideia do modelo avançado)
    limite_horas_anual = models.IntegerField(default=120)
    horas_utilizadas = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def horas_disponiveis(self):
        return self.limite_horas_anual - self.horas_utilizadas

# Sinal para criar o profile automaticamente
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ServidorProfile.objects.create(user=instance)
    instance.servidorprofile.save()


class Edital(models.Model):
    STATUS_CHOICES = [
        ('Rascunho', 'Rascunho'),
        ('Aguardando Homologação', 'Aguardando Homologação'),
        ('Homologado', 'Homologado'),
        ('Recusado', 'Recusado'),
        ('Ativo', 'Ativo'),
        ('Finalizado', 'Finalizado'),
    ]
    
    numero_edital = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    unidade_demandante_nome = models.CharField(max_length=255) # Campo de texto simples por enquanto
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Rascunho')
    valor_empenho = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Relacionamentos
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='editais_criados')
    homologado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='editais_homologados', null=True, blank=True)
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Edital'
        verbose_name_plural = 'Editais'
        ordering = ['-data_inicio']
        
    def __str__(self):
        return f"{self.numero_edital} - {self.titulo}"


class Atividade(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Relacionamentos
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='atividades')
    servidores_alocados = models.ManyToManyField(User, related_name='atividades_alocadas', blank=True)

    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'
        ordering = ['nome']
        
    def __str__(self):
        return self.nome


class LancamentoHoras(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Aprovado', 'Aprovado'),
        ('Recusado', 'Recusado'),
    ]
    
    # Relacionamentos
    servidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lancamentos')
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='lancamentos')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='lancamentos')
    
    # Dados do lançamento
    data = models.DateField()
    horas = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.1)])
    descricao_justificativa = models.TextField()
    
    # Status e validação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')
    comentario_recusa = models.TextField(blank=True)
    validado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='lancamentos_validados', null=True, blank=True)
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lançamento de Hora'
        verbose_name_plural = 'Lançamentos de Horas'
        ordering = ['-data']
        
    def __str__(self):
        return f"Lançamento de {self.servidor.username} em {self.data}"