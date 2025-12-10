from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decouple import config

from emails.models import Email
from emails.management.commands.verificar_rotinas_diarias import Command
from core.models import Projeto, Pesquisador

class RegistroLogTestCase(TestCase):
    def setUp(self):
        self.pesquisador1 = Pesquisador.objects.create(nome="Teste1", email=config('EMAIL_TEST_1'), telefone="123456789")
        self.pesquisador2 = Pesquisador.objects.create(nome="Teste2", email=config('EMAIL_TEST_2'), telefone="987654321")
        self.pesquisador3 = Pesquisador.objects.create(nome="Teste3", email=config('EMAIL_TEST_3'), telefone="987612345")
        self.projeto1 = Projeto.objects.create(titulo="Projeto Teste 1", pesquisador=self.pesquisador1)
        self.projeto2 = Projeto.objects.create(titulo="Projeto Teste 2", pesquisador=self.pesquisador1)
        self.projeto3 = Projeto.objects.create(titulo="Projeto Teste 3", pesquisador=self.pesquisador2)
        self.projeto4 = Projeto.objects.create(titulo="Projeto Teste 4", pesquisador=self.pesquisador2)
        self.projeto5 = Projeto.objects.create(titulo="Projeto Teste 5", pesquisador=self.pesquisador3)


        hoje = timezone.now()

        self.data_a = hoje - timedelta(days=2)
        self.data_b = hoje - timedelta(days=1)
        self.data_c = hoje

        self.log1 = Logs.objects.create(
            nome_log="A",
            processo="proc1",
            parametros_usados={"x": 10},
            projeto=self.projeto,
            concluiu=True,
            horario=self.data_a
        )
        self.log2 = Logs.objects.create(
            nome_log="B",
            processo="proc2",
            parametros_usados={"x": 20, "z": "Hello, World!"},
            projeto=self.projeto,
            concluiu=False,
            msgErro="Falha",
            horario=self.data_b
        )
        self.log3 = Logs.objects.create(
            nome_log="A",
            processo="proc3",
            parametros_usados={"y": 99},
            projeto=None,
            concluiu=True,
            horario=self.data_c
        )