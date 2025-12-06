from django.contrib import admin
from .models import Projeto, Parecer, Pesquisador, Emenda

@admin.register(Pesquisador)
class PesquisadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone')
    search_fields = ('nome', 'email')

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    """
    Visualização dos Projetos no painel admin.
    """
    list_display = ('titulo', 'caae', 'pesquisador', 'status', 'relator_designado')
    list_filter = ('status', 'data_submissao', 'rel_final')
    search_fields = ('titulo', 'caae', 'pesquisador__nome')
    readonly_fields = ('data_submissao', 'data_aprovacao')

@admin.register(Emenda)
class EmendaAdmin(admin.ModelAdmin):
    """
    Visualização das Emendas.
    Nota: Emendas usam 'relator_parecer', não 'relator'.
    """
    list_display = ('titulo', 'projeto', 'status', 'data_submissao', 'relator_parecer')
    list_filter = ('status', 'data_submissao')
    search_fields = ('titulo', 'projeto__titulo')
    readonly_fields = ('data_submissao', 'data_parecer')

@admin.register(Parecer)
class ParecerAdmin(admin.ModelAdmin):
    """
    Visualização dos Pareceres de Projetos.
    Nota: Pareceres usam 'relator'.
    """
    list_display = ('projeto', 'relator', 'decisao', 'data_parecer')
    list_filter = ('decisao',)
    search_fields = ('projeto__titulo', 'relator__username')
    readonly_fields = ('data_parecer',)