from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, Historico
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
    total_itens = produtos.count()
    alerta = sum(1 for p in produtos if p.saldo <= p.minimo)
    em_uso = sum(p.em_uso for p in produtos if 'FERRAMENT' in p.categoria.upper())
    
    context = {
        'total_itens': total_itens,
        'itens_alerta': alerta,
        'ferramentas_em_uso': int(em_uso),
        'produtos': produtos[:10], # Mostrar apenas os 10 primeiros no dashboard
    }
    return render(request, 'almox/index.html', context)

@login_required
def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        categoria = request.POST.get('categoria', 'DIVERSOS').upper().strip()
        local = request.POST.get('local', 'ALMOX 1')
        saldo = Decimal(request.POST.get('saldo', '0').replace(',', '.'))
        minimo = Decimal(request.POST.get('minimo', '0').replace(',', '.'))
        obs = request.POST.get('observacao', '')

        # Verificar se existe
        existente = None
        for p in Produto.objects.all():
            if normalizar(p.nome) == normalizar(nome):
                existente = p
                break
        
        if existente:
            existente.saldo += saldo
            existente.save()
            messages.success(request, f"Estoque atualizado para: {existente.nome}")
        else:
            # Gerar Código
            prefixos = {"FERRAMENTAS": "FER", "DIVERSOS": "DIV", "DEFENSIVOS": "DEF", "ADUBO": "ADU"}
            prefixo = prefixos.get(categoria, categoria[:3])
            ultimo = Produto.objects.filter(codigo__startswith=prefixo).order_by('-codigo').first()
            if ultimo:
                num = int(ultimo.codigo.split('-')[1]) + 1
            else:
                num = 1
            codigo = f"{prefixo}-{str(num).zfill(4)}"
            
            Produto.objects.create(
                codigo=codigo, nome=nome, categoria=categoria,
                saldo=saldo, local=local, minimo=minimo, observacao=obs
            )
            messages.success(request, f"Produto cadastrado com sucesso: {codigo}")
        
        return redirect('cadastro')

    return render(request, 'almox/cadastro.html')

@login_required
def movimentacao(request):
    if request.method == 'POST':
        p_ids = request.POST.getlist('produto')
        quantidades = request.POST.getlist('quantidade')
        responsavel = request.POST.get('responsavel')
        
        if not responsavel:
            messages.error(request, "Informe o responsável!")
            return redirect('movimentacao')

        for p_id, q in zip(p_ids, quantidades):
            if not p_id or not q: continue
            
            produto = Produto.objects.get(id=p_id)
            qtd = Decimal(q.replace(',', '.'))
            
            if qtd > produto.saldo:
                messages.error(request, f"Estoque insuficiente para {produto.nome}")
                return redirect('movimentacao')
            
            saldo_anterior = produto.saldo
            produto.saldo -= qtd
            
            if 'FERRAMENT' in produto.categoria.upper():
                produto.em_uso += qtd
            
            produto.save()
            
            Historico.objects.create(
                produto_info=f"{produto.codigo} - {produto.nome}",
                tipo=produto.categoria,
                quantidade=qtd,
                responsavel=responsavel,
                saldo_anterior=saldo_anterior,
                saldo_atual=produto.saldo,
                local=produto.local
            )
        
        messages.success(request, "Movimentação realizada com sucesso!")
        return redirect('index')

    produtos = Produto.objects.all()
    return render(request, 'almox/movimentacao.html', {'produtos': produtos})

@login_required
def relatorios(request):
    registros = Historico.objects.all()
    return render(request, 'almox/relatorios.html', {'registros': registros})

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Usuário ou senha inválidos")
    return render(request, 'almox/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
