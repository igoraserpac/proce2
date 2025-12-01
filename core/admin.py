# core/admin.py

from django.contrib import admin
from .models import Projeto, Parecer, Pesquisador

@admin.register(Pesquisador)
class PesquisadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone')
    search_fields = ('nome', 'email')

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    """
    Personaliza a visualização dos Projetos no admin.
    """
    list_display = ('titulo', 'caae', 'pesquisador', 'status', 'relator_designado')
    list_filter = ('status', 'data_submissao', 'rel_final')
    search_fields = ('titulo', 'caae', 'pesquisador__nome')
    readonly_fields = ('data_submissao', 'data_aprovacao')

@admin.register(Parecer)
class ParecerAdmin(admin.ModelAdmin):
    """
    Personaliza a visualização dos Pareceres no admin.
    """
    list_display = ('projeto', 'relator', 'decisao', 'data_parecer')
    list_filter = ('decisao',)
    search_fields = ('projeto__titulo', 'relator__username')
    readonly_fields = ('data_parecer',)