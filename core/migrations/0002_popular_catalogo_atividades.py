# core/migrations/0002_popular_catalogo_atividades.py

from django.db import migrations

# Lista de atividades extraída da Resolução CONSU Nº 67, de 28 de julho de 2023
ATIVIDADES = [
    # a) Instrutoria
    {"grupo": "Instrutoria", "nome": "Instrutoria em curso de formação de carreiras", "valor_hora": 40.55},
    {"grupo": "Instrutoria", "nome": "Instrutoria em curso de desenvolvimento e aperfeiçoamento", "valor_hora": 40.55},
    {"grupo": "Instrutoria", "nome": "Instrutoria em curso de treinamento", "valor_hora": 40.55},
    {"grupo": "Instrutoria", "nome": "Tutoria em curso à distância", "valor_hora": 27.71},
    {"grupo": "Instrutoria", "nome": "Instrutoria em curso gerencial", "valor_hora": 40.55},
    {"grupo": "Instrutoria", "nome": "Instrutoria em curso de pós-graduação", "valor_hora": 40.55},
    {"grupo": "Instrutoria", "nome": "Orientação de monografia", "valor_hora": 42.05},
    {"grupo": "Instrutoria", "nome": "Instrutoria em curso de educação de jovens e adultos", "valor_hora": 14.33},
    {"grupo": "Instrutoria", "nome": "Coordenação técnica e pedagógica", "valor_hora": 27.71},
    {"grupo": "Instrutoria", "nome": "Elaboração de material didático", "valor_hora": 27.71},
    {"grupo": "Instrutoria", "nome": "Elaboração de material multimídia para curso à distância", "valor_hora": 42.05},
    {"grupo": "Instrutoria", "nome": "Atividade de conferencista e de palestrante", "valor_hora": 42.03},
    
    # b) Banca Examinadora
    {"grupo": "Banca", "nome": "Exame oral", "valor_hora": 22.37},
    {"grupo": "Banca", "nome": "Análise curricular", "valor_hora": 15.28},
    {"grupo": "Banca", "nome": "Correção de prova discursiva", "valor_hora": 28.12},
    {"grupo": "Banca", "nome": "Elaboração de questão de prova subjetiva", "valor_hora": 22.94},
    {"grupo": "Banca", "nome": "Elaboração de questão de prova objetiva", "valor_hora": 45.88},
    {"grupo": "Banca", "nome": "Julgamento de recurso prova objetiva", "valor_hora": 19.96},
    {"grupo": "Banca", "nome": "Julgamento de recurso prova subjetiva", "valor_hora": 30.68},
    {"grupo": "Banca", "nome": "Prova prática", "valor_hora": 22.37},
    {"grupo": "Banca", "nome": "Análise crítica de questão de prova", "valor_hora": 28.11},
    {"grupo": "Banca", "nome": "Julgamento de concurso de monografia", "valor_hora": 28.12},
    
    # c) Logística
    {"grupo": "Logistica", "nome": "Planejamento", "valor_hora": 81.93},
    {"grupo": "Logistica", "nome": "Coordenação", "valor_hora": 81.93},
    {"grupo": "Logistica", "nome": "Supervisão (Logística)", "valor_hora": 60.47}, # Nome ajustado para diferenciar
    {"grupo": "Logistica", "nome": "Execução", "valor_hora": 40.52},
    
    # d) Aplicação de Prova
    {"grupo": "Aplicacao", "nome": "Aplicação", "valor_hora": 18.77},
    {"grupo": "Aplicacao", "nome": "Fiscalização", "valor_hora": 34.56},
    {"grupo": "Aplicacao", "nome": "Supervisão (Aplicação de Prova)", "valor_hora": 44.69}, # Nome ajustado para diferenciar
]

def popular_atividades(apps, schema_editor):
    TipoAtividade = apps.get_model('core', 'TipoAtividade')
    for atividade_data in ATIVIDADES:
        TipoAtividade.objects.create(**atividade_data)

def remover_atividades(apps, schema_editor):
    TipoAtividade = apps.get_model('core', 'TipoAtividade')
    TipoAtividade.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(popular_atividades, reverse_code=remover_atividades),
    ]