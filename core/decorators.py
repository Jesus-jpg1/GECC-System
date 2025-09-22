from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    """
    Decorator para checar se o usuário tem uma das funções permitidas.
    Redireciona para o painel se não tiver.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                if request.user.servidorprofile.funcao in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('painel')
            except AttributeError:
                
                return redirect('painel')
        return wrapper
    return decorator

# Criando decoradores específicos para cada função
unidade_demandante_required = role_required(allowed_roles=['Unidade Demandante'])
servidor_required = role_required(allowed_roles=['Servidor'])
prodgep_required = role_required(allowed_roles=['PRODGEP/PROPEG'])