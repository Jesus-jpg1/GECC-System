# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Edital, Atividade, TipoAtividade, LancamentoHoras, Unidade, ServidorProfile


class EditalForm(forms.ModelForm):
    class Meta:
        model = Edital
        fields = [
            "numero_edital",
            "titulo",
            "descricao",
            "unidade_demandante_nome",
            "data_inicio",
            "data_fim",
            "valor_empenho",
        ]
        widgets = {
            "data_inicio": forms.DateInput(attrs={"type": "date"}),
            "data_fim": forms.DateInput(attrs={"type": "date"}),
        }


class AtividadeForm(forms.ModelForm):
    tipo = forms.ModelChoiceField(
        queryset=TipoAtividade.objects.order_by("valor_hora"),
        label="Selecione o Tipo da Atividade",
    )

    class Meta:
        model = Atividade
        fields = ["tipo", "descricao"]


class AlocarServidorForm(forms.Form):
    servidores = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(servidorprofile__funcao="Servidor"),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Selecione os Servidores para Alocar nesta Atividade",
    )


class LancamentoHorasForm(forms.ModelForm):
    horas = forms.CharField(
        label='Horas Trabalhadas',
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 02:30'}),
        help_text="Use o formato HH:MM (horas:minutos)."
    )

    def __init__(self, *args, **kwargs):
        self.atividade = kwargs.pop('atividade', None)
        super().__init__(*args, **kwargs)

    def clean_horas(self):
        # --- PARTE NOVA: Conversão de HH:MM para Decimal ---
        horas_str = self.cleaned_data.get('horas')
        
        if ':' not in horas_str:
            raise ValidationError("Formato inválido. Use HH:MM (ex: 02:30).")
        try:
            horas, minutos = map(int, horas_str.split(':'))
            if not (0 <= minutos < 60):
                raise ValueError()
            decimal_horas = horas + (minutos / 60.0)
        except (ValueError, TypeError):
            raise ValidationError("Formato inválido. Use apenas números no formato HH:MM.")
        
        # --- PARTE EXISTENTE: Validação do Orçamento ---
        if not self.atividade:
            raise ValidationError("Atividade não encontrada para validação de orçamento.")

        edital = self.atividade.edital
        valor_hora = self.atividade.tipo.valor_hora
        custo_atual = decimal_horas * float(valor_hora)
        
        total_gasto = 0
        lancamentos_do_edital = LancamentoHoras.objects.filter(edital=edital).exclude(status='Recusado')
        for lancamento in lancamentos_do_edital:
            total_gasto += lancamento.horas * lancamento.atividade.tipo.valor_hora
            
        saldo_restante = edital.valor_empenho - total_gasto

        if custo_atual > saldo_restante:
            raise ValidationError(
                f"Este lançamento de R$ {custo_atual:.2f} ultrapassa o saldo de empenho restante do edital, que é de R$ {saldo_restante:.2f}."
            )

        return round(decimal_horas, 2) 

    class Meta:
        model = LancamentoHoras
        fields = ['data', 'descricao_justificativa']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'data': 'Data da Realização',
            'descricao_justificativa': 'Descrição da Atividade/Justificativa',
        }

class AdicionarServidorForm(forms.Form):
    # Campos do modelo User
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150)
    email = forms.EmailField(label="Email")
    username = forms.CharField(label="Nome de Usuário (Login)", max_length=150)

    # Campos do modelo ServidorProfile
    funcao = forms.ChoiceField(label="Função no Sistema", choices=ServidorProfile.FUNCAO_CHOICES)
    cpf = forms.CharField(label="CPF", max_length=14)
    siape = forms.CharField(label="SIAPE", max_length=20)
    titulacao = forms.ChoiceField(label="Titulação", choices=ServidorProfile.TITULACAO_CHOICES)
    unidade = forms.ModelChoiceField(label="Unidade Organizacional", queryset=Unidade.objects.all())

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Um usuário com este nome de login já existe.")
        return username

    def save(self):
        # Cria o User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password='password123' # Senha padrão, o usuário pode alterar depois
        )

        # Atualiza o ServidorProfile criado pelo signal
        profile = user.servidorprofile
        profile.funcao = self.cleaned_data['funcao']
        profile.cpf = self.cleaned_data['cpf']
        profile.siape = self.cleaned_data['siape']
        profile.titulacao = self.cleaned_data['titulacao']
        profile.unidade = self.cleaned_data['unidade']
        profile.status = 'Aguardando Homologação' # Já entra como homologado, pois foi criado por um admin
        profile.save()

        return user