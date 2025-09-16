# core/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .decorators import unidade_demandante_required, servidor_required, prodgep_required
from .models import Edital, Atividade, LancamentoHoras, ServidorProfile
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
def listar_editais(request):
    if request.user.servidorprofile.funcao != "Unidade Demandante":
        return redirect("painel")

    editais = Edital.objects.filter(criado_por=request.user).order_by("-created_at")

    context = {"editais": editais}
    return render(request, "listar_editais.html", context)


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

    # Regra: Só permite editar se o status for "Rascunho"
    if edital.status != "Rascunho":
        return redirect("detalhes_edital", pk=edital.pk)

    if request.method == "POST":
        # Passamos 'instance=edital' para que o form saiba que está editando um objeto existente
        form = EditalForm(request.POST, instance=edital)
        if form.is_valid():
            form.save()
            return redirect("detalhes_edital", pk=edital.pk)
    else:
        # Ao carregar a página (GET), o form já vem preenchido com os dados do edital
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
            # O método set() atualiza o ManyToManyField com a nova lista
            atividade.servidores_alocados.set(servidores_selecionados)
            return redirect("detalhes_edital", pk=edital.pk)
    else:
        # Preenche o formulário com os servidores já alocados
        form = AlocarServidorForm(
            initial={"servidores": atividade.servidores_alocados.all()}
        )

    context = {"form": form, "atividade": atividade, "edital": edital}
    return render(request, "alocar_servidores.html", context)


@login_required
def enviar_homologacao(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    # Segurança e regra de negócio
    if edital.criado_por != request.user:
        return redirect("listar_editais")

    # Ação acontece apenas via POST e se o edital for um Rascunho
    if request.method == "POST" and edital.status == "Rascunho":
        edital.status = "Aguardando Homologação"
        edital.save()
        # No futuro, podemos adicionar uma mensagem de sucesso aqui
        return redirect("detalhes_edital", pk=edital.pk)

    # Se a requisição não for POST ou o status não for Rascunho, apenas redireciona
    return redirect("detalhes_edital", pk=edital.pk)


@login_required
def aprovar_horas(request):
    if request.user.servidorprofile.funcao != "Unidade Demandante":
        return redirect("painel")

    # Busca todos os lançamentos pendentes de editais criados pelo usuário logado
    lancamentos_pendentes = LancamentoHoras.objects.filter(
        edital__criado_por=request.user, status="Pendente"
    ).order_by("data")

    context = {"lancamentos": lancamentos_pendentes}
    return render(request, "aprovar_horas.html", context)


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

            return redirect("lancar_horas")
    else:
        form = LancamentoHorasForm()

    context = {
        "atividades_alocadas": atividades_alocadas,
        "form": form,
    }
    return render(request, "lancar_horas.html", context)


@login_required
def historico_lancamentos(request):
    if request.user.servidorprofile.funcao != "Servidor":
        return redirect("painel")

    meus_lancamentos = LancamentoHoras.objects.filter(servidor=request.user).order_by(
        "-data"
    )

    context = {"lancamentos": meus_lancamentos}
    return render(request, "historico_lancamentos.html", context)


# VIEW PARA LISTAR OS EDITAIS PENDENTES DE HOMOLOGAÇÃO
@login_required
def homologar_editais(request):
    if request.user.servidorprofile.funcao != "PRODGEP/PROPEG":
        return redirect("painel")

    editais_pendentes = Edital.objects.filter(status="Aguardando Homologação").order_by(
        "data_inicio"
    )

    context = {"editais": editais_pendentes}
    return render(request, "homologar_editais.html", context)


# VIEW PARA A AÇÃO DE HOMOLOGAR (APROVAR) EDITAL
@login_required
def registrar_homologacao_edital(request, pk):
    if request.user.servidorprofile.funcao != "PRODGEP/PROPEG":
        return redirect("painel")

    edital = get_object_or_404(Edital, pk=pk)

    if request.method == "POST":
        edital.status = "Homologado"
        edital.homologado_por = request.user
        edital.save()
    return redirect("homologar_editais")


# VIEW PARA A AÇÃO DE RECUSAR EDITAL
@login_required
def registrar_recusa_edital(request, pk):
    if request.user.servidorprofile.funcao != "PRODGEP/PROPEG":
        return redirect("painel")

    edital = get_object_or_404(Edital, pk=pk)

    if request.method == "POST":
        edital.status = "Recusado"
        edital.homologado_por = request.user
        edital.save()
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
    return redirect("homologar_servidores")

@login_required
@prodgep_required
def auditoria_horas(request):
    # Filtro para os status que interessam à auditoria
    status_auditaveis = ['Aprovado', 'Recusado', 'Homologado', 'Revertido']

    # Otimização: Prepara uma busca de todos os lançamentos relevantes
    lancamentos_para_prefetch = LancamentoHoras.objects.filter(
        status__in=status_auditaveis
    ).select_related('servidor', 'atividade__tipo', 'validado_por')

    # Busca os Editais que têm lançamentos com os status acima
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
