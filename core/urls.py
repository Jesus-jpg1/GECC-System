# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Nossa URL principal do painel (ex: http://127.0.0.1:8000/painel/)
    path('painel/', views.painel, name='painel'),
]