from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, Historico, ControleVeiculo
from decimal import Decimal
import re
import unicodedata

def normalizar(texto):
    if not texto: return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", texto)

@login_required
def index(request):
    produtos = Produto.objects.all()
    context = {
        'total_itens': produtos.count(),
        'itens_alerta': sum(1 for p in produtos if p.saldo <= p.minimo),
        'ferramentas_em_uso': int(sum(p.em_uso for p in produtos if 'FERRAMENT' in p.categoria.upper())),
        'produtos': produtos,
    }
    return render(request, 'almox/index.html', context)

@login_required
def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        categoria = request.POST.get('categoria', 'DIVERSOS').upper().strip()
        saldo = Decimal(request.POST.get('saldo', '0').replace(',', '.'))
        minimo = Decimal(request.POST.get('minimo', '0').replace(',', '.'))
        
        existente = None
        for p in Produto.objects.all():
            if normalizar(p.nome) == normalizar(nome):
                existente = p; break
        
        if existente:
            existente.saldo += saldo; existente.save()
            messages.success(request, f"Estoque atualizado: {existente.nome}")
        else:
            prefixos = {"FERRAMENTAS": "FER", "DIVERSOS": "DIV", "DEFENSIVOS": "DEF", "ADUBO": "ADU"}
            prefixo = prefixos.get(categoria, categoria[:3])
            ultimo = Produto.objects.filter(codigo__startswith=prefixo).order_by('-codigo').first()
            num = (int(ultimo.codigo.split('-')[1]) + 1) if ultimo else 1
            codigo = f"{prefixo}-{str(num).zfill(4)}"
            Produto.objects.create(codigo=codigo, nome=nome, categoria=categoria, saldo=saldo, minimo=minimo)
            messages.success(request, f"Produto cadastrado: {codigo}")
        return redirect('cadastro')
    return render(request, 'almox/cadastro.html')

@login_required
def movimentacao(request):
    if request.method == 'POST':
        p_ids = request.POST.getlist('produto')
        quantidades = request.POST.getlist('quantidade')
        responsavel = request.POST.get('responsavel')
        for p_id, q in zip(p_ids, quantidades):
            if not p_id or not q: continue
            produto = Produto.objects.get(id=p_id)
            qtd = Decimal(q.replace(',', '.'))
            if qtd > produto.saldo:
                messages.error(request, f"Sem estoque: {produto.nome}"); return redirect('movimentacao')
            saldo_anterior = produto.saldo
            produto.saldo -= qtd
            if 'FERRAMENT' in produto.categoria.upper(): produto.em_uso += qtd
            produto.save()
            Historico.objects.create(produto_info=f"{produto.codigo} - {produto.nome}", tipo=produto.categoria, quantidade=qtd, responsavel=responsavel, saldo_anterior=saldo_anterior, saldo_atual=produto.saldo, local=produto.local)
        messages.success(request, "Saída realizada!"); return redirect('index')
    return render(request, 'almox/movimentacao.html', {'produtos': Produto.objects.all()})

@login_required
def relatorios(request):
    return render(request, 'almox/relatorios.html', {'registros': Historico.objects.all()})

@login_required
def veiculos(request):
    if request.method == 'POST':
        ControleVeiculo.objects.create(
            veiculo=request.POST.get('veiculo'),
            ultima_manutencao=request.POST.get('ultima_manutencao'),
            proxima_manutencao=request.POST.get('proxima_manutencao'),
            tipo=request.POST.get('tipo'),
            responsavel=request.POST.get('responsavel')
        )
        messages.success(request, "Registro de veículo salvo!")
        return redirect('veiculos')
    
    registros = ControleVeiculo.objects.all()
    context = {
        'registros': registros,
        'count_ok': sum(1 for r in registros if r.status == "OK"),
        'count_alerta': sum(1 for r in registros if r.status == "ALERTA"),
        'count_atrasado': sum(1 for r in registros if r.status == "ATRASADO"),
    }
    return render(request, 'almox/veiculos.html', context)

def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user: login(request, user); return redirect('index')
        messages.error(request, "Inválido")
    return render(request, 'almox/login.html')

def logout_view(request): logout(request); return redirect('login')
