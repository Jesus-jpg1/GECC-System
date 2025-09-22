from django.contrib import admin
from .models import ServidorProfile, Edital, Atividade, LancamentoHoras, TipoAtividade

# Registrando os modelos para que apareçam na interface de administração
admin.site.register(ServidorProfile)
admin.site.register(Edital)
admin.site.register(Atividade)
admin.site.register(LancamentoHoras)
admin.site.register(TipoAtividade)
