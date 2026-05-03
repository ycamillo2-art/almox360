from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('movimentacao/', views.movimentacao, name='movimentacao'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('veiculos/', views.veiculos, name='veiculos'),
    path('abastecimento/', views.abastecimento, name='abastecimento'),
    path('manutencao/', views.manutencao, name='manutencao'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
