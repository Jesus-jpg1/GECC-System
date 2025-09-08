# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Edital

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
    
@login_required
def listar_editais(request):
    if request.user.servidorprofile.funcao != 'Unidade Demandante':
        return redirect('painel')
    
    editais = Edital.objects.filter(criado_por=request.user).order_by('-created_at')

    context = {
        'editais': editais
    }
    return render(request, 'listar_editais.html', context)