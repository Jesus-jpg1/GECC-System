# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.painel, name='painel'),
    path('editais/', views.listar_editais, name='listar_editais'),
    path('editais/novo/', views.criar_edital, name='criar_edital'),
    path('editais/<int:pk>/', views.detalhes_edital, name='detalhes_edital'),
    path('editais/<int:pk>/editar/', views.editar_edital, name='editar_edital'),
    path('editais/<int:edital_pk>/atividades/adicionar/', views.adicionar_atividade, name='adicionar_atividade'),
    path('atividades/<int:pk>/remover/', views.remover_atividade, name='remover_atividade'),
    path('atividades/<int:pk>/editar/', views.editar_atividade, name='editar_atividade'),
    path('atividades/<int:pk>/alocar/', views.alocar_servidores, name='alocar_servidores'),
    path('editais/<int:pk>/enviar/', views.enviar_homologacao, name='enviar_homologacao'),
    path('horas/aprovar/', views.aprovar_horas, name='aprovar_horas'),
    path('horas/<int:pk>/registrar-aprovacao/', views.registrar_aprovacao_hora, name='registrar_aprovacao_hora'),
    path('horas/<int:pk>/registrar-recusa/', views.registrar_recusa_hora, name='registrar_recusa_hora'),
]