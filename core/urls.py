# core/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    # URLs de Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('projeto/<int:pk>/designar/', views.designar_relator, name='designar_relator'),
    path('projeto/<int:pk>/parecer/', views.dar_parecer, name='dar_parecer'),
    path('projeto/<int:pk>/', views.detalhe_projeto, name='detalhe_projeto'),
]