import os
import sys
import json
import django

# Adicionar o diretório atual ao sys.path para encontrar o almox360_root
sys.path.append(os.getcwd())

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
# Forçar a URL do banco PostgreSQL
os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'

django.setup()

from almox.models import Produto

def restaurar():
    with open('dados_migracao_real.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    produtos_json = data.get('produtos', [])
    restaurados = 0
    pulados = 0

    for item in produtos_json:
        # Verificar se o produto já existe pelo código ou nome para não duplicar
        codigo = str(item['codigo'])
        nome = item['nome']
        
        obj, created = Produto.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nome': nome,
                'categoria': item['categoria'],
                'saldo': float(item['saldo']),
                'local': item['local'],
                'minimo': float(item['minimo']),
                'observacao': item['observacao'],
                'em_uso': float(item['em_uso'])
            }
        )
        
        if created:
            restaurados += 1
        else:
            pulados += 1
            
    print(f"Restauração concluída: {restaurados} itens recuperados, {pulados} já existiam.")

if __name__ == "__main__":
    restaurar()
