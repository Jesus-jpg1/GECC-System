# core/forms.py
from django import forms
from .models import Edital, Atividade, TipoAtividade

class EditalForm(forms.ModelForm):
    class Meta:
        model = Edital
        fields = [
            'numero_edital',
            'titulo',
            'descricao',
            'unidade_demandante_nome',
            'data_inicio',
            'data_fim',
            'valor_empenho',
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

class AtividadeForm(forms.ModelForm):
    # Transforma a ForeignKey em um campo de seleção
    tipo = forms.ModelChoiceField(
        queryset=TipoAtividade.objects.order_by('valor_hora'),
        label="Selecione o Tipo da Atividade"
    )

    class Meta:
        model = Atividade
        fields = ['tipo']