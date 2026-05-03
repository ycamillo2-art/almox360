import os
import django
import json
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
django.setup()

from almox.models import Produto, Historico, ControleVeiculo

def importar():
    with open('dados_migracao.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # 1. Importar Produtos
    print(f"Importando {len(dados['produtos'])} produtos...")
    for p in dados['produtos']:
        Produto.objects.update_or_create(
            codigo=p['codigo'],
            defaults={
                'nome': p['nome'],
                'categoria': p['categoria'],
                'saldo': Decimal(p['saldo']),
                'local': p['local'],
                'minimo': Decimal(p['minimo']),
                'observacao': p['observacao'],
                'em_uso': Decimal(p['em_uso'])
            }
        )

    # 2. Importar Histórico
    print(f"Importando {len(dados['historico'])} registros de histórico...")
    for h in dados['historico']:
        Historico.objects.create(
            data=h['data'],
            produto_info=h['produto'],
            tipo=h['tipo'],
            quantidade=Decimal(h['quantidade']),
            responsavel=h['responsavel'],
            saldo_anterior=Decimal(h['saldo_anterior']),
            saldo_atual=Decimal(h['saldo_atual']),
            local=h['local'],
            devolvido=h['devolvido']
        )

    # 3. Importar Veículos
    print(f"Importando {len(dados['veiculos'])} registros de veículos...")
    for v in dados['veiculos']:
        ControleVeiculo.objects.create(
            veiculo=v['veiculo'],
            ultima_manutencao=v['ultima_manutencao'],
            proxima_manutencao=v['proxima_manutencao'],
            tipo=v['tipo_servico'],
            responsavel=v['usuario']
        )
    
    print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == '__main__':
    importar()
