# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Edital, Atividade, TipoAtividade, LancamentoHoras


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
    # Transforma a ForeignKey em um campo de seleção
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

    def __init__(self, *args, **kwargs):
        # Recebe a atividade da view para poder fazer os cálculos
        self.atividade = kwargs.pop('atividade', None)
        super().__init__(*args, **kwargs)

    def clean_horas(self):
        horas_lancadas = self.cleaned_data.get('horas')

        if not self.atividade:
            raise ValidationError("Atividade não encontrada.")

        edital = self.atividade.edital
        valor_hora = self.atividade.tipo.valor_hora

        # Custo deste lançamento
        custo_atual = horas_lancadas * valor_hora

        # Calcula o total já gasto ou comprometido no edital
        total_gasto = 0
        lancamentos_do_edital = LancamentoHoras.objects.filter(edital=edital).exclude(status='Recusado')
        for lancamento in lancamentos_do_edital:
            total_gasto += lancamento.horas * lancamento.atividade.tipo.valor_hora

        saldo_restante = edital.valor_empenho - total_gasto

        if custo_atual > saldo_restante:
            raise ValidationError(
                f"Este lançamento de R$ {custo_atual:.2f} ultrapassa o saldo de empenho restante do edital, que é de R$ {saldo_restante:.2f}."
            )

        return horas_lancadas

    class Meta:
        model = LancamentoHoras
        fields = ['data', 'horas', 'descricao_justificativa']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'data': 'Data da Realização',
            'horas': 'Horas Trabalhadas (ex: 2.5)',
            'descricao_justificativa': 'Descrição da Atividade/Justificativa',
        }
