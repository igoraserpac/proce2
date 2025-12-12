from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Projeto, Parecer
from emails.gerenciadorEmails import GerenciadorEmails, TipoRelatorio

class Command(BaseCommand):
    help = 'Executa rotinas diárias de verificação de e-mails (Pendências e Relatórios)'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando rotinas diárias de email...")
        
        self.verificar_projetos_aprovados()
        self.verificar_projetos_pendentes()
        
        self.stdout.write(self.style.SUCCESS("Rotinas finalizadas."))

    def verificar_projetos_aprovados(self):
        """
        Regra: 
        - 180 dias após aprovação: cobrar relatório parcial.
        - 365 dias após aprovação: cobrar relatório final ou parcial.
        """
        hoje = timezone.now().date()
        
        # Datas alvo
        data_180_dias = hoje - timedelta(days=180)
        data_365_dias = hoje - timedelta(days=365)

        # Buscar projetos aprovados nessas datas exatas
        projetos_180 = Projeto.objects.filter(status='aprovado', data_aprovacao=data_180_dias, rel_parc=False)
        projetos_365 = Projeto.objects.filter(status='aprovado', data_aprovacao=data_365_dias) # Final cobra mesmo se entregou parcial antes

        # Envio 180 dias
        for proj in projetos_180:
            self.enviar_cobranca_relatorio(proj, 30, TipoRelatorio.PARCIAL.value)

        # Envio 365 dias (1 ano)
        for proj in projetos_365:
            # Se já entregou o final, não precisa cobrar
            if not proj.rel_final:
                self.enviar_cobranca_relatorio(proj, 30, TipoRelatorio.QUALQUER.value)

    def enviar_cobranca_relatorio(self, projeto, dias_prazo, tipo_texto):
        try:
            self.stdout.write(f"Enviando cobrança de relatório ({tipo_texto}) para {projeto.titulo}")
            GerenciadorEmails.notificacao_relatorio_aprovado(
                nome_pesquisador=projeto.pesquisador.nome,
                nome_pesquisa=projeto.titulo,
                email_destinatario=projeto.pesquisador.email,
                dias_restantes=dias_prazo,
                tipo_relatorio=tipo_texto
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao enviar para {projeto.id}: {e}"))

    def verificar_projetos_pendentes(self):
        """
        Regra:
        - Pesquisador tem 30 dias para corrigir.
        - Enviar emails diários nos 5 últimos dias (dia 26, 27, 28, 29, 30).
        - Após 30 dias, enviar email pedindo retirada.
        """
        projetos_pendentes = Projeto.objects.filter(status='pendente')
        hoje = timezone.now() # Usamos datetime completo para comparar com o Parecer (que é DateTimeField)

        prazo_limite_dias = 30
        inicio_aviso_dias = 25 # Começa a avisar no dia 26 (quando faltam 5 dias)

        for projeto in projetos_pendentes:
            # Descobre quando ficou pendente pegando o último parecer
            ultimo_parecer = projeto.pareceres.filter(decisao='pendente').order_by('-data_parecer').first()
            
            if not ultimo_parecer:
                continue

            # Calcula quantos dias se passaram desde o parecer
            dias_corridos = (hoje - ultimo_parecer.data_parecer).days
            dias_restantes = prazo_limite_dias - dias_corridos

            enviar = False
            
            # Situação A: Faltam 5 dias ou menos (e ainda está no prazo)
            if 0 <= dias_restantes <= 5: 
                # Note: se dias_restantes for 5, significa que passaram 25 dias.
                # O requisito diz "nos 5 últimos dias".
                enviar = True
            
            # Situação B: Estourou o prazo (dias_restantes < 0)
            elif dias_restantes == -1: 
                enviar = True

            if enviar:
                try:
                    print("try")
                    self.stdout.write(f"Enviando aviso de pendência para {projeto.titulo}. Restam: {dias_restantes} dias.")
                    
                    # Usa o método estático que você já tem no gerenciadorEmails.py
                    # Esse método já sabe formatar o texto se dias_restantes <= 0
                    GerenciadorEmails.notificacao_relatorio_pendente(
                        nome_pesquisador=projeto.pesquisador.nome,
                        nome_pesquisa=projeto.titulo,
                        email_destinatario=projeto.pesquisador.email,
                        dias_restantes=dias_restantes if dias_restantes > 0 else 0
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro ao enviar pendência para {projeto.id}: {e}"))

