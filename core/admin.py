from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ServidorProfile, Edital, Atividade, LancamentoHoras, TipoAtividade, Unidade

# 1. Define uma classe "inline" para o ServidorProfile.
# Isto diz ao Django: "mostre o ServidorProfile dentro de outra página de admin".
class ServidorProfileInline(admin.StackedInline):
    model = ServidorProfile
    can_delete = False
    verbose_name_plural = 'Perfil do Servidor'

# 2. Cria uma nova classe de admin para o User que inclui o inline acima.
class UserAdmin(BaseUserAdmin):
    inlines = [ServidorProfileInline]

# 3. Desregistra o admin padrão do User e registra a nossa nova versão.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 4. Registra os outros modelos normalmente.
# O ServidorProfile não precisa ser registrado aqui, pois ele já aparece dentro do User.
admin.site.register(Edital)
admin.site.register(TipoAtividade)
admin.site.register(Atividade)
admin.site.register(LancamentoHoras)
admin.site.register(Unidade)