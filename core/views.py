from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from .models import Projeto, User 
from .forms import DesignarRelatorForm, ParecerForm
from django.utils import timezone

from functools import wraps

def grupo_requerido(nome_grupo):
    """
    Um decorator que verifica se o usuário pertence a um grupo específico.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.groups.filter(name=nome_grupo).exists():
                # Se não pertencer, retorna "Proibido"
                return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Função auxiliar que já tínhamos (mantenha ela)
def is_grupo(user, nome_grupo):
    return user.groups.filter(name=nome_grupo).exists()

@login_required # Garante que apenas usuários logados acessem esta página
def dashboard(request):
    """
    Página inicial (Dashboard) que muda conforme o grupo do usuário.
    """
    contexto = {}
    
    # Se for do grupo 'Gestores'
    if is_grupo(request.user, 'Gestores'):
        # 1. Pegue todos os projetos que estão com status 'novo' (precisam de relator)
        projetos_para_designar = Projeto.objects.filter(status='novo')
        
        # 2. Pegue todos os projetos que já estão em análise ou pendentes
        projetos_em_analise = Projeto.objects.filter(status__in=['em_analise', 'pendente'])
        
        # 3. Pegue projetos finalizados
        projetos_concluidos = Projeto.objects.filter(status__in=['aprovado', 'reprovado'])

        contexto['projetos_para_designar'] = projetos_para_designar
        contexto['projetos_em_analise'] = projetos_em_analise
        contexto['projetos_concluidos'] = projetos_concluidos

        # Define qual template HTML deve ser usado
        template_renderizar = 'core/dashboard_gestor.html'

    # Se for do grupo 'Relatores'
    elif is_grupo(request.user, 'Relatores'):
        # 1. Pegue os projetos que foram designados PARA ESTE relator e estão 'em_analise'
        projetos_para_analisar = Projeto.objects.filter(
            relator_designado=request.user, 
            status='em_analise'
        )
        
        # 2. Pegue os projetos que este relator já analisou (aprovou, reprovou, pendente)
        meus_projetos_concluidos = Projeto.objects.filter(
            relator_designado=request.user
        ).exclude(status='em_analise') # Exclui os que ainda estão para analisar

        contexto['projetos_para_analisar'] = projetos_para_analisar
        contexto['meus_projetos_concluidos'] = meus_projetos_concluidos
        
        template_renderizar = 'core/dashboard_relator.html'
    
    # Se não for de nenhum grupo (ex: superusuário ou erro)
    else:
        contexto['mensagem_erro'] = "Seu usuário não está configurado em um grupo (Gestor ou Relator)."
        template_renderizar = 'core/dashboard_generico.html'

    return render(request, template_renderizar, contexto)

@login_required
@grupo_requerido('Gestores')
def designar_relator(request, pk):
    """
    Página para um Gestor designar um relator a um projeto específico (pk).
    """
    projeto = get_object_or_404(Projeto, pk=pk, status='novo')

    if request.method == 'POST':
        form = DesignarRelatorForm(request.POST, instance=projeto)
        if form.is_valid():
            projeto_salvo = form.save(commit=False)
            # Ao designar um relator, o status muda para 'Em Análise'
            projeto_salvo.status = 'em_analise' 
            projeto_salvo.save()
            
            # Redireciona de volta ao Dashboard
            return redirect('dashboard') 
    else:
        # GET: Mostra o formulário
        form = DesignarRelatorForm(instance=projeto)

    contexto = {
        'form': form,
        'projeto': projeto
    }
    return render(request, 'core/designar_relator.html', contexto)

@login_required
@grupo_requerido('Relatores') # Apenas Relatores
def dar_parecer(request, pk):
    """
    Página para um Relator dar seu parecer sobre um projeto específico (pk).
    """
    projeto = get_object_or_404(Projeto, pk=pk)

    # --- VERIFICAÇÃO DE SEGURANÇA ---
    # O usuário logado é o relator designado?
    if request.user != projeto.relator_designado:
        return HttpResponseForbidden("Você não é o relator designado para este projeto.")
    
    # O projeto está no status correto para receber um parecer?
    if projeto.status != 'em_analise':
        return HttpResponseForbidden(f"Este projeto está com status '{projeto.get_status_display()}' e não pode receber pareceres no momento.")

    if request.method == 'POST':
        form = ParecerForm(request.POST)
        if form.is_valid():
            parecer = form.save(commit=False)
            parecer.projeto = projeto
            parecer.relator = request.user
            parecer.save()

            projeto.status = parecer.decisao
            
            # Se a decisão for APROVADO, salva a data de hoje na data_aprovacao
            if parecer.decisao == 'aprovado':
                projeto.data_aprovacao = timezone.now().date()
            else:
                projeto.data_aprovacao = None

            projeto.save()
            
            return redirect('dashboard')
    else:
        # GET: Mostra o formulário vazio
        form = ParecerForm()

    contexto = {
        'form': form,
        'projeto': projeto
    }
    return render(request, 'core/dar_parecer.html', contexto)

@login_required
def detalhe_projeto(request, pk):
    """
    Exibe os detalhes de um projeto e seu histórico de pareceres.
    """
    projeto = get_object_or_404(Projeto, pk=pk)
    
    # Segurança básica: Relatores só veem seus próprios projetos
    if is_grupo(request.user, 'Relatores') and projeto.relator_designado != request.user:
         return HttpResponseForbidden("Você não tem permissão para visualizar este projeto.")

    # Busca todos os pareceres desse projeto, do mais recente para o mais antigo
    pareceres = projeto.pareceres.all().order_by('-data_parecer')

    contexto = {
        'projeto': projeto,
        'pareceres': pareceres
    }
    return render(request, 'core/detalhe_projeto.html', contexto)