# core/views.py
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.urls import reverse
from .decorators import unidade_demandante_required, servidor_required, prodgep_required
from .models import Edital, Atividade, LancamentoHoras, ServidorProfile, Notificacao
from .forms import EditalForm, AtividadeForm, AlocarServidorForm, LancamentoHorasForm


@login_required
def painel(request):
    try:
        funcao_usuario = request.user.servidorprofile.funcao
    except AttributeError:
        return render(request, "painel_padrao.html")

    if funcao_usuario == "Unidade Demandante":
        return render(request, "painel_unidade_demandante.html")
    elif funcao_usuario == "Servidor":
        return render(request, "painel_servidor.html")
    elif funcao_usuario == "PRODGEP/PROPEG":
        return render(request, "painel_prodgep.html")
    else:
        return render(request, "painel_padrao.html")

@login_required
@unidade_demandante_required
def listar_editais(request):
    lista_de_editais = Edital.objects.filter(criado_por=request.user)

    # --- LÓGICA DE ORDENAÇÃO ---
    sort_param = request.GET.get('sort', '-created_at')

    allowed_sort_fields = ['numero_edital', 'titulo', 'created_at', 'status']

    sort_field = sort_param.lstrip('-') 

    if sort_field in allowed_sort_fields:
        lista_de_editais = lista_de_editais.order_by(sort_param)
    else:
        lista_de_editais = lista_de_editais.order_by('-created_at')

    # --- LÓGICA DE PAGINAÇÃO (continua a mesma) ---
    paginator = Paginator(lista_de_editais, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_sort': sort_param
    }
    return render(request, 'listar_editais.html', context)


@login_required
def criar_edital(request):
    if request.user.servidorprofile.funcao != "Unidade Demandante":
        return redirect("painel")

    if request.method == "POST":
        form = EditalForm(request.POST)
        if form.is_valid():
            novo_edital = form.save(commit=False)
            novo_edital.criado_por = request.user
            novo_edital.save()
            messages.success(request, 'Edital criado com sucesso!')
            return redirect("listar_editais")
    else:
        form = EditalForm()

    context = {"form": form}
    return render(request, "criar_edital.html", context)


@login_required
def detalhes_edital(request, pk):
    # Primeiro, buscamos o edital sem checar o dono
    edital = get_object_or_404(Edital, pk=pk)

    # Agora, fazemos a checagem de permissão manualmente
    is_owner = (edital.criado_por == request.user)
    is_auditor = (request.user.servidorprofile.funcao == 'PRODGEP/PROPEG')

    # Se o usuário NÃO for o dono E TAMBÉM NÃO for um auditor, redirecionamos
    if not is_owner and not is_auditor:
        return redirect('painel')

    # Se passou na checagem, continua normalmente
    atividades = edital.atividades.all().order_by('tipo__valor_hora')
    context = {'edital': edital, 'atividades': atividades}
    return render(request, 'detalhes_edital.html', context)


@login_required
def editar_edital(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    if edital.criado_por != request.user:
        return redirect("listar_editais")

    if edital.status != "Rascunho":
        return redirect("detalhes_edital", pk=edital.pk)

    if request.method == "POST":
        form = EditalForm(request.POST, instance=edital)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edital atualizado com sucesso!')
            return redirect("detalhes_edital", pk=edital.pk)
    else:
        form = EditalForm(instance=edital)

    context = {"form": form, "edital": edital}
    return render(request, "editar_edital.html", context)


@login_required
def adicionar_atividade(request, edital_pk):
    edital = get_object_or_404(Edital, pk=edital_pk)

    if edital.criado_por != request.user:
        return redirect("listar_editais")

    if request.method == "POST":
        form = AtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.edital = edital  # Associa a atividade ao edital correto
            atividade.save()
            messages.success(request, 'Atividade adicionada ao edital com sucesso!')
            return redirect("detalhes_edital", pk=edital.pk)
    else:
        form = AtividadeForm()

    context = {"form": form, "edital": edital}
    return render(request, "adicionar_atividade.html", context)


@login_required
def remover_atividade(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    edital_pk = atividade.edital.pk

    # Segurança: Garante que o usuário é o dono do edital da atividade
    if atividade.edital.criado_por != request.user:
        return redirect("listar_editais")

    # A remoção só acontece se a requisição for do tipo POST
    if request.method == "POST":
        atividade.delete()
        messages.warning(request, 'Atividade removida com sucesso.')
        return redirect("detalhes_edital", pk=edital_pk)

    # Se for GET, apenas redireciona de volta para os detalhes
    return redirect("detalhes_edital", pk=edital_pk)


@login_required
def editar_atividade(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    edital = atividade.edital

    # Segurança
    if edital.criado_por != request.user:
        return redirect("listar_editais")

    if request.method == "POST":
        form = AtividadeForm(request.POST, instance=atividade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Atividade atualizada com sucesso!')
            return redirect("detalhes_edital", pk=edital.pk)
    else:
        form = AtividadeForm(instance=atividade)

    context = {"form": form, "edital": edital, "atividade": atividade}
    return render(request, "editar_atividade.html", context)


@login_required
def alocar_servidores(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    edital = atividade.edital

    # Segurança
    if edital.criado_por != request.user:
        return redirect("listar_editais")

    if request.method == "POST":
        form = AlocarServidorForm(request.POST)
        if form.is_valid():
            servidores_selecionados = form.cleaned_data["servidores"]
            atividade.servidores_alocados.set(servidores_selecionados)
            messages.success(request, 'Servidores alocados com sucesso!')
            return redirect("detalhes_edital", pk=edital.pk)
    else:
        form = AlocarServidorForm(
            initial={"servidores": atividade.servidores_alocados.all()}
        )

    context = {"form": form, "atividade": atividade, "edital": edital}
    return render(request, "alocar_servidores.html", context)


@login_required
def enviar_homologacao(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    if edital.criado_por != request.user:
        return redirect("listar_editais")

    if request.method == "POST" and edital.status == "Rascunho":
        edital.status = "Aguardando Homologação"
        edital.save()
        messages.info(request, 'Edital enviado para homologação.')
        return redirect("detalhes_edital", pk=edital.pk)

    return redirect("detalhes_edital", pk=edital.pk)

@login_required
@unidade_demandante_required
def aprovar_horas(request):
    lancamentos_list = LancamentoHoras.objects.filter(
        edital__criado_por=request.user, 
        status='Pendente'
    )

    sort_param = request.GET.get('sort', '-data') 
    allowed_sort_fields = [
        'data', 'servidor__first_name', 'edital__numero_edital', 
        'atividade__tipo__nome', 'horas'
    ]

    allowed_sort_fields.extend(['-' + field for field in allowed_sort_fields])

    if sort_param in allowed_sort_fields:
        lancamentos_list = lancamentos_list.order_by(sort_param)

    paginator = Paginator(lancamentos_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_sort': sort_param
    }
    return render(request, 'aprovar_horas.html', context)


# VIEW PARA A AÇÃO DE APROVAR
@login_required
def registrar_aprovacao_hora(request, pk):
    lancamento = get_object_or_404(LancamentoHoras, pk=pk)
    
    if lancamento.edital.criado_por != request.user:
        return redirect("listar_editais")

    if request.method == "POST":
        lancamento.status = "Aprovado"
        lancamento.validado_por = request.user
        lancamento.save()
        messages.success(request, 'Lançamento de horas APROVADO.')

        Notificacao.objects.create(
            usuario=lancamento.servidor,
            mensagem=f'Suas {lancamento.horas} horas na atividade "{lancamento.atividade.tipo.nome}" foram APROVADAS.',
            link=reverse('historico_lancamentos')
        )
    return redirect("aprovar_horas")


# VIEW PARA A AÇÃO DE RECUSAR
@login_required
def registrar_recusa_hora(request, pk):
    lancamento = get_object_or_404(LancamentoHoras, pk=pk)

    # Segurança
    if lancamento.edital.criado_por != request.user:
        return redirect("listar_editais")

    if request.method == "POST":
        lancamento.status = "Recusado"
        lancamento.validado_por = request.user
        motivo = request.POST.get("motivo_recusa", "")
        lancamento.comentario_recusa = motivo
        lancamento.save()
        messages.error(request, 'Lançamento de horas RECUSADO.')
    
        Notificacao.objects.create(
            usuario=lancamento.servidor,
            mensagem=f'Suas {lancamento.horas} horas na atividade "{lancamento.atividade.tipo.nome}" foram RECUSADAS.',
            link=reverse('historico_lancamentos')
        )
    return redirect("aprovar_horas")


@login_required
def lancar_horas(request):
    if request.user.servidorprofile.funcao != "Servidor":
        return redirect("painel")

    atividades_alocadas = Atividade.objects.filter(servidores_alocados=request.user)

    if request.method == "POST":
        form = LancamentoHorasForm(request.POST)
        if form.is_valid():

            atividade_id = request.POST.get("atividade_id")
            atividade = get_object_or_404(Atividade, pk=atividade_id)

            lancamento = form.save(commit=False)
            lancamento.servidor = request.user
            lancamento.atividade = atividade
            lancamento.edital = atividade.edital
            lancamento.save()
            messages.success(request, 'Horas lançadas com sucesso! Aguardando aprovação.')

            return redirect("lancar_horas")
    else:
        form = LancamentoHorasForm()

    context = {
        "atividades_alocadas": atividades_alocadas,
        "form": form,
    }
    return render(request, "lancar_horas.html", context)


@login_required
@servidor_required
def historico_lancamentos(request):
    # Busca a lista base de lançamentos do usuário
    lancamentos_list = LancamentoHoras.objects.filter(servidor=request.user)

    # Lógica de Ordenação
    sort_param = request.GET.get('sort', '-data')
    allowed_sort_fields = [
        'data', 'edital__numero_edital', 'atividade__tipo__nome', 'horas', 'status'
    ]
    sort_field_clean = sort_param.lstrip('-')
    if sort_field_clean in allowed_sort_fields:
        lancamentos_list = lancamentos_list.order_by(sort_param)

    # Lógica de Paginação
    paginator = Paginator(lancamentos_list, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_sort': sort_param
    }
    return render(request, 'historico_lancamentos.html', context)

# VIEW PARA LISTAR OS EDITAIS PENDENTES DE HOMOLOGAÇÃO
@login_required
@prodgep_required
def homologar_editais(request):
    editais_list = Edital.objects.filter(status='Aguardando Homologação')

    # Lógica de Ordenação
    sort_param = request.GET.get('sort', 'data_inicio')
    allowed_sort_fields = ['numero_edital', 'titulo', 'unidade_demandante_nome', 'criado_por__first_name']

    # Adiciona a versão descendente dos campos
    allowed_sort_fields.extend(['-' + field for field in allowed_sort_fields])

    if sort_param in allowed_sort_fields:
        editais_list = editais_list.order_by(sort_param)

    # Lógica de Paginação
    paginator = Paginator(editais_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_sort': sort_param
    }
    return render(request, 'homologar_editais.html', context)


# VIEW PARA A AÇÃO DE HOMOLOGAR (APROVAR) EDITAL
@login_required
@prodgep_required
def registrar_homologacao_edital(request, pk):
    edital = get_object_or_404(Edital, pk=pk)
    if request.method == "POST":
        edital.status = "Homologado"
        edital.homologado_por = request.user
        edital.save()
        messages.success(request, 'Edital HOMOLOGADO com sucesso.')

        Notificacao.objects.create(
            usuario=edital.criado_por,
            mensagem=f'O edital "{edital.numero_edital}" foi homologado.',
            link=reverse('detalhes_edital', args=[edital.pk])
        )

    return redirect("homologar_editais")


# VIEW PARA A AÇÃO DE RECUSAR EDITAL
@login_required
@prodgep_required
def registrar_recusa_edital(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    if request.method == "POST":

        motivo = request.POST.get('motivo_recusa', 'Recusado pela auditoria PRODGEP/PROPEG.')
        
        edital.status = "Recusado"
        edital.homologado_por = request.user
        edital.justificativa_recusa = motivo
        edital.save()
        
        messages.error(request, f'O edital "{edital.numero_edital}" foi recusado.')

        Notificacao.objects.create(
            usuario=edital.criado_por, # A notificação é para quem criou o edital
            mensagem=f'O edital "{edital.numero_edital}" foi recusado.',
            link=reverse('detalhes_edital', args=[edital.pk])
        )
    
    return redirect("homologar_editais")


@login_required
def homologar_servidores(request):

    if request.user.servidorprofile.funcao != "PRODGEP/PROPEG":
        return redirect("painel")

    servidores_pendentes = ServidorProfile.objects.filter(
        status="Aguardando Homologação"
    )

    context = {"servidores_pendentes": servidores_pendentes}
    return render(request, "homologar_servidores.html", context)


@login_required
def aprovar_servidor(request, pk):
    if request.user.servidorprofile.funcao != "PRODGEP/PROPEG":
        return redirect("painel")

    perfil_servidor = get_object_or_404(ServidorProfile, pk=pk)

    if request.method == "POST":
        perfil_servidor.status = "Homologado"
        perfil_servidor.save()
        messages.success(request, 'Servidor HOMOLOGADO com sucesso.')
    return redirect("homologar_servidores")


# VIEW PARA A AÇÃO DE RECUSAR O SERVIDOR
@login_required
def recusar_servidor(request, pk):
    if request.user.servidorprofile.funcao != "PRODGEP/PROPEG":
        return redirect("painel")

    perfil_servidor = get_object_or_404(ServidorProfile, pk=pk)

    if request.method == "POST":
        perfil_servidor.status = "Recusado"
        perfil_servidor.save()
        messages.error(request, 'Servidor RECUSADO.')
    return redirect("homologar_servidores")

@login_required
@prodgep_required
def auditoria_horas(request):
    status_auditaveis = ['Aprovado', 'Recusado', 'Homologado', 'Revertido']

    lancamentos_para_prefetch = LancamentoHoras.objects.filter(
        status__in=status_auditaveis
    ).select_related('servidor', 'atividade__tipo', 'validado_por')

    editais_para_auditoria = Edital.objects.prefetch_related(
        Prefetch('lancamentos', queryset=lancamentos_para_prefetch, to_attr='lancamentos_auditaveis'),
        'atividades__tipo'
    ).filter(
        lancamentos__status__in=status_auditaveis
    ).distinct().order_by('-data_inicio')

    context = {
        'editais': editais_para_auditoria
    }
    return render(request, 'auditoria_horas.html', context)

@login_required
def detalhes_atividade(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    if atividade.edital.criado_por != request.user:
        return redirect('listar_editais')

    context = {'atividade': atividade}
    return render(request, 'detalhes_atividade.html', context)

@login_required
@prodgep_required
def exportar_auditoria_pdf(request):
    status_auditaveis = ['Aprovado', 'Recusado', 'Homologado', 'Revertido']
    lancamentos = LancamentoHoras.objects.filter(
        status__in=status_auditaveis
    ).select_related('servidor', 'edital', 'atividade__tipo', 'validado_por').order_by('-data')

    context = {
        'lancamentos': lancamentos
    }

    # 1. Renderiza o template HTML em uma string
    html_string = render_to_string('relatorios/auditoria_pdf.html', context)

    # 2. Converte a string HTML em um objeto WeasyPrint
    html = HTML(string=html_string)

    # 3. Gera o PDF em memória
    pdf = html.write_pdf()

    # 4. Cria uma resposta HTTP com o PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_auditoria_horas.pdf"'

    return response

@login_required
@prodgep_required
def exportar_edital_pdf(request, edital_pk):
    edital = get_object_or_404(Edital, pk=edital_pk)

    status_auditaveis = ['Aprovado', 'Recusado', 'Homologado', 'Revertido']
    lancamentos = LancamentoHoras.objects.filter(
        edital=edital,
        status__in=status_auditaveis
    ).select_related('servidor', 'atividade__tipo', 'validado_por').order_by('servidor__first_name', 'data')

    context = {
        'lancamentos': lancamentos,
        'edital': edital
    }

    html_string = render_to_string('relatorios/edital_pdf.html', context)
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_edital_{edital.numero_edital.replace("/", "-")}.pdf"'

    return response

@login_required
def meu_perfil(request):
    return render(request, 'meu_perfil.html')

@login_required
def get_notificacoes_nao_lidas(request):
    notificacoes = Notificacao.objects.filter(usuario=request.user, lida=False)
    count = notificacoes.count()    

    # Constrói uma lista de dicionários com os dados das notificações 
    notificacoes_data = [{
        'id': n.id,
        'mensagem': n.mensagem,
        'link': n.link
    } for n in notificacoes]

    return JsonResponse({'count': count, 'notificacoes': notificacoes_data})

@login_required
def marcar_notificacoes_como_lidas(request):
    if request.method == 'POST':
        Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)