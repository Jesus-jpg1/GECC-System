# Dentro do seu novo arquivo de migração (ex: core/migrations/0002_popular_catalogo_atividades.py)

from django.db import migrations

# [cite_start]Dados extraídos da Resolução CONSU Nº 67, de 28 de julho de 2023 [cite: 12]
ATIVIDADES = [
    # a) Instrutoria
    [cite_start]{"grupo": "Instrutoria", "nome": "Instrutoria em curso de formação de carreiras", "valor_hora": 40.55}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Instrutoria em curso de desenvolvimento e aperfeiçoamento", "valor_hora": 40.55}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Instrutoria em curso de treinamento", "valor_hora": 40.55}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Tutoria em curso à distância", "valor_hora": 27.71}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Instrutoria em curso gerencial", "valor_hora": 40.55}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Instrutoria em curso de pós-graduação", "valor_hora": 40.55}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Orientação de monografia", "valor_hora": 42.05}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Instrutoria em curso de educação de jovens e adultos", "valor_hora": 14.33}, # [cite: 111]
    [cite_start]{"grupo": "Instrutoria", "nome": "Coordenação técnica e pedagógica", "valor_hora": 27.71}, # [cite: 112]
    [cite_start]{"grupo": "Instrutoria", "nome": "Elaboração de material didático", "valor_hora": 27.71}, # [cite: 112]
    [cite_start]{"grupo": "Instrutoria", "nome": "Elaboração de material multimídia para curso à distância", "valor_hora": 42.05}, # [cite: 112]
    [cite_start]{"grupo": "Instrutoria", "nome": "Atividade de conferencista e de palestrante", "valor_hora": 42.03}, # [cite: 112]
    
    # b) Banca Examinadora
    [cite_start]{"grupo": "Banca", "nome": "Exame oral", "valor_hora": 22.37}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Análise curricular", "valor_hora": 15.28}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Correção de prova discursiva", "valor_hora": 28.12}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Elaboração de questão de prova subjetiva", "valor_hora": 22.94}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Elaboração de questão de prova objetiva", "valor_hora": 45.88}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Julgamento de recurso prova objetiva", "valor_hora": 19.96}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Julgamento de recurso prova subjetiva", "valor_hora": 30.68}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Prova prática", "valor_hora": 22.37}, # [cite: 114]
    [cite_start]{"grupo": "Banca", "nome": "Análise crítica de questão de prova", "valor_hora": 28.11}, # [cite: 115]
    [cite_start]{"grupo": "Banca", "nome": "Julgamento de concurso de monografia", "valor_hora": 28.12}, # [cite: 115]
    
    # c) Logística
    [cite_start]{"grupo": "Logistica", "nome": "Planejamento", "valor_hora": 81.93}, # [cite: 117]
    [cite_start]{"grupo": "Logistica", "nome": "Coordenação", "valor_hora": 81.93}, # [cite: 117]
    [cite_start]{"grupo": "Logistica", "nome": "Supervisão (Logística)", "valor_hora": 60.47}, # [cite: 117]
    [cite_start]{"grupo": "Logistica", "nome": "Execução", "valor_hora": 40.52}, # [cite: 117]
    
    # d) Aplicação de Prova
    [cite_start]{"grupo": "Aplicacao", "nome": "Aplicação", "valor_hora": 18.77}, # [cite: 120]
    [cite_start]{"grupo": "Aplicacao", "nome": "Fiscalização", "valor_hora": 34.56}, # [cite: 120]
    [cite_start]{"grupo": "Aplicacao", "nome": "Supervisão (Aplicação de Prova)", "valor_hora": 44.69}, # [cite: 120]
]

def popular_atividades(apps, schema_editor):
    TipoAtividade = apps.get_model('core', 'TipoAtividade')
    for atividade_data in ATIVIDADES:
        # get_or_create evita duplicatas se a migração for rodada novamente
        TipoAtividade.objects.get_or_create(nome=atividade_data['nome'], defaults=atividade_data)

def remover_atividades(apps, schema_editor):
    TipoAtividade = apps.get_model('core', 'TipoAtividade')
    for atividade_data in ATIVIDADES:
        TipoAtividade.objects.filter(nome=atividade_data['nome']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'), # Garanta que este número corresponde à sua migração anterior
    ]

    operations = [
        migrations.RunPython(popular_atividades, reverse_code=remover_atividades),
    ]