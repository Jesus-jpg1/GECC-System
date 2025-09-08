# core/forms.py
from django import forms
from .models import Edital

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