# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.painel, name='painel'),
    path('editais/', views.listar_editais, name='listar_editais'),
    path('editais/novo/', views.criar_edital, name='criar_edital'),
    # A nova URL captura um número inteiro (int) da URL e o chama de 'pk'
    path('editais/<int:pk>/', views.detalhes_edital, name='detalhes_edital'),
]