# core/views.py
from django.shortcuts import render, redirect, get_object_or_404 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Edital, Atividade
from .forms import EditalForm, AtividadeForm

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

@login_required
def criar_edital(request):
    if request.user.servidorprofile.funcao != 'Unidade Demandante':
        return redirect('painel')

    if request.method == 'POST':
        form = EditalForm(request.POST)
        if form.is_valid():
            novo_edital = form.save(commit=False)
            novo_edital.criado_por = request.user
            novo_edital.save()
            return redirect('listar_editais')
    else:
        form = EditalForm()
    
    context = {
        'form': form
    }
    return render(request, 'criar_edital.html', context)

@login_required
def detalhes_edital(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    if edital.criado_por != request.user:
        return redirect('listar_editais')
    
    #Busca todas as atividades relacionadas a este edital
    atividades = edital.atividades.all().order_by('tipo__valor_hora')

    context = {
        'edital': edital,
        'atividades': atividades #Passa a lista de atividades para o template
    }
    return render(request, 'detalhes_edital.html', context)

@login_required
def editar_edital(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    if edital.criado_por != request.user:
        return redirect('listar_editais')

    # Regra: Só permite editar se o status for "Rascunho"
    if edital.status != 'Rascunho':
        return redirect('detalhes_edital', pk=edital.pk)

    if request.method == 'POST':
        # Passamos 'instance=edital' para que o form saiba que está editando um objeto existente
        form = EditalForm(request.POST, instance=edital)
        if form.is_valid():
            form.save()
            return redirect('detalhes_edital', pk=edital.pk)
    else:
        # Ao carregar a página (GET), o form já vem preenchido com os dados do edital
        form = EditalForm(instance=edital)

    context = {
        'form': form,
        'edital': edital
    }
    return render(request, 'editar_edital.html', context)

@login_required
def adicionar_atividade(request, edital_pk):
    edital = get_object_or_404(Edital, pk=edital_pk)

    if edital.criado_por != request.user:
        return redirect('listar_editais')

    if request.method == 'POST':
        form = AtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.edital = edital # Associa a atividade ao edital correto
            atividade.save()
            return redirect('detalhes_edital', pk=edital.pk)
    else:
        form = AtividadeForm()

    context = {
        'form': form,
        'edital': edital
    }
    return render(request, 'adicionar_atividade.html', context)

@login_required
def remover_atividade(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    edital_pk = atividade.edital.pk

    # Segurança: Garante que o usuário é o dono do edital da atividade
    if atividade.edital.criado_por != request.user:
        return redirect('listar_editais')

    # A remoção só acontece se a requisição for do tipo POST
    if request.method == 'POST':
        atividade.delete()
        return redirect('detalhes_edital', pk=edital_pk)
    
    # Se for GET, apenas redireciona de volta para os detalhes
    return redirect('detalhes_edital', pk=edital_pk)

@login_required
def editar_atividade(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    edital = atividade.edital

    # Segurança
    if edital.criado_por != request.user:
        return redirect('listar_editais')

    if request.method == 'POST':
        form = AtividadeForm(request.POST, instance=atividade)
        if form.is_valid():
            form.save()
            return redirect('detalhes_edital', pk=edital.pk)
    else:
        form = AtividadeForm(instance=atividade)

    context = {
        'form': form,
        'edital': edital,
        'atividade': atividade
    }
    return render(request, 'editar_atividade.html', context)