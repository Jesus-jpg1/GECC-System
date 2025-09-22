# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

# NOVO MODELO PARA UNIDADES ORGANIZACIONAIS
class Unidade(models.Model):
    sigla = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Unidade Organizacional"
        verbose_name_plural = "Unidades Organizacionais"
        ordering = ['sigla']

    def __str__(self):
        return self.sigla


class ServidorProfile(models.Model):
    FUNCAO_CHOICES = [
        ("Unidade Demandante", "Unidade Demandante"),
        ("PRODGEP/PROPEG", "PRODGEP/PROPEG"),
        ("Servidor", "Servidor"),
    ]
    STATUS_CHOICES = [
        ("Aguardando Homologação", "Aguardando Homologação"),
        ("Homologado", "Homologado"),
        ("Recusado", "Recusado"),
    ]
    # NOVO CAMPO DE TITULAÇÃO
    TITULACAO_CHOICES = [
        ('Graduação', 'Graduação'),
        ('Especialização', 'Especialização'),
        ('Mestrado', 'Mestrado'),
        ('Doutorado', 'Doutorado'),
        ('Pós-Doutorado', 'Pós-Doutorado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    siape = models.CharField(max_length=20, unique=True, null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    setor = models.CharField(max_length=100, blank=True)
    funcao = models.CharField(max_length=30, choices=FUNCAO_CHOICES, default="Servidor")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Aguardando Homologação")
    telefone = models.CharField(max_length=20, blank=True)
    limite_horas_anual = models.IntegerField(default=120)
    horas_utilizadas = models.IntegerField(default=0)
    
    # NOVOS CAMPOS ADICIONADOS
    titulacao = models.CharField(max_length=20, choices=TITULACAO_CHOICES, null=True, blank=True)
    unidade = models.ForeignKey(Unidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='servidores')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def horas_disponiveis(self):
        return self.limite_horas_anual - self.horas_utilizadas


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ServidorProfile.objects.create(user=instance)
    # A linha abaixo foi removida da função 'create' para evitar chamadas duplas
    instance.servidorprofile.save()


class Edital(models.Model):
    STATUS_CHOICES = [
        ("Rascunho", "Rascunho"),
        ("Aguardando Homologação", "Aguardando Homologação"),
        ("Homologado", "Homologado"),
        ("Recusado", "Recusado"),
        ("Ativo", "Ativo"),
        ("Finalizado", "Finalizado"),
    ]
    numero_edital = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    unidade_demandante_nome = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Rascunho")
    justificativa_recusa = models.TextField(blank=True, null=True)
    valor_empenho = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="editais_criados")
    homologado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="editais_homologados",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Edital"
        verbose_name_plural = "Editais"
        ordering = ["-data_inicio"]

    def __str__(self):
        return f"{self.numero_edital} - {self.titulo}"


class TipoAtividade(models.Model):
    GRUPO_CHOICES = [
        ("Instrutoria", "Instrutoria"),
        ("Banca", "Banca Examinadora"),
        ("Logistica", "Logística"),
        ("Aplicacao", "Aplicação de Prova"),
    ]
    # NOVO CAMPO DE VÍNCULO
    VINCULO_CHOICES = [
        ('Concurso', 'Concurso Público'),
        ('Processo', 'Processo Seletivo'),
        ('Ambos', 'Ambos'),
    ]

    grupo = models.CharField(max_length=20, choices=GRUPO_CHOICES)
    nome = models.CharField(max_length=255, unique=True)
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    # NOVO CAMPO ADICIONADO
    vinculo = models.CharField(max_length=10, choices=VINCULO_CHOICES, default='Ambos')

    class Meta:
        verbose_name = "Tipo de Atividade (Catálogo)"
        verbose_name_plural = "Tipos de Atividade (Catálogo)"
        ordering = ["grupo", "nome"]

    def __str__(self):
        return f"{self.nome} (R$ {self.valor_hora:.2f}/h)"


class Atividade(models.Model):
    tipo = models.ForeignKey(TipoAtividade, on_delete=models.PROTECT, related_name="atividades_criadas")
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name="atividades")
    # NOVO CAMPO DE DESCRIÇÃO
    descricao = models.TextField()
    servidores_alocados = models.ManyToManyField(User, related_name="atividades_alocadas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Atividade do Edital"
        verbose_name_plural = "Atividades do Edital"

    def __str__(self):
        return self.tipo.nome


class LancamentoHoras(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Aprovado", "Aprovado"),
        ("Recusado", "Recusado"),
        ('Homologado', 'Homologado'),
        ('Revertido', 'Revertido pela PRODGEP'),
    ]
    servidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lancamentos")
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name="lancamentos")
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name="lancamentos")
    data = models.DateField()
    horas = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.1)])
    descricao_justificativa = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pendente")
    comentario_recusa = models.TextField(blank=True)
    validado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="lancamentos_validados",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lançamento de Hora"
        verbose_name_plural = "Lançamentos de Horas"
        ordering = ["-data"]

    def __str__(self):
        return f"Lançamento de {self.servidor.username} em {self.data}"
    
class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificação para {self.usuario.username}: {self.mensagem[:30]}..."