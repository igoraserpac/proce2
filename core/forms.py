# core/forms.py (CRIE ESTE ARQUIVO)

from django import forms
from django.contrib.auth.models import User, Group
from .models import Projeto, Parecer

class DesignarRelatorForm(forms.ModelForm):
    """
    Formulário para o Gestor designar um relator a um projeto.
    """
    
    # Sobrescrevemos o campo 'relator_designado'
    relator_designado = forms.ModelChoiceField(
        queryset=None, # O queryset será definido no __init__
        label="Selecione o Relator",
        empty_label="-- Nenhum --"
    )

    class Meta:
        model = Projeto
        fields = ['relator_designado'] # Apenas este campo será editável

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtramos o queryset para mostrar APENAS usuários
        # que pertencem ao grupo 'Relatores'.
        try:
            grupo_relatores = Group.objects.get(name='Relatores')
            self.fields['relator_designado'].queryset = grupo_relatores.user_set.all()
        except Group.DoesNotExist:
            # Se o grupo não existir, o dropdown ficará vazio
            self.fields['relator_designado'].queryset = User.objects.none()

class ParecerForm(forms.ModelForm):
    """
    Formulário para o Relator dar seu parecer sobre um projeto.
    """
    class Meta:
        model = Parecer
        # O relator só precisa preencher a decisão e a justificativa
        fields = ['decisao', 'justificativa']
        widgets = {
            'decisao': forms.RadioSelect(choices=Parecer.DECISAO_CHOICES),
            'justificativa': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['justificativa'].required = True
        self.fields['decisao'].label = "Qual a sua decisão sobre este projeto?"
        self.fields['justificativa'].label = "Justificativa (obrigatório)"

