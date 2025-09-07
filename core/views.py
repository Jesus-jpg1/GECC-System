# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def painel(request):    
    try:
        funcao_usuario = request.user.servidorprofile.funcao
    except AttributeError:
        return render(request, 'painel_padrao.html')

    if funcao_usuario == 'Unidade Demandante':
        return render(request, 'painel_unidade_demandante.html')
    elif funcao_usuario == 'Servidor':
        return render(request, 'painel_servidor.html')
    elif funcao_usuario == 'PRODGEP/PROPEG':
        return render(request, 'painel_prodgep.html')
    else:
        return render(request, 'painel_padrao.html')