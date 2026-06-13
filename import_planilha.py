import os
import sys
import django
import pandas as pd
from django.utils import timezone

# Adicionar o diretório atual ao sys.path para encontrar o almox360_root
sys.path.append(os.getcwd())

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
# Se houver DATABASE_URL no ambiente (Render), o Django usará. 
# Para garantir que use o banco correto, vamos forçar a URL que temos se estivermos local
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'

django.setup()

from almox.models import Produto

def importar():
    df = pd.read_csv('dados_planilha.csv')
    cont_def = Produto.objects.filter(categoria='DEFENSIVOS').count()
    cont_adb = Produto.objects.filter(categoria='ADUBO').count()
    
    criados = 0
    atualizados = 0

    for _, row in df.iterrows():
        nome = str(row['ÍTEM']).strip()
        qtd_str = str(row['QUANTIDADE']).replace(',', '.')
        try:
            quantidade = float(qtd_str) if qtd_str and qtd_str != 'nan' else 0
        except:
            quantidade = 0
            
        local = str(row['ALMOXARIFADO']).strip()
        
        # Regra do usuário
        if local == 'ALMOX 4':
            categoria = 'DEFENSIVOS'
            prefixo = 'DEF'
            cont_def += 1
            num = cont_def
        elif local == 'ALMOX 5':
            categoria = 'ADUBO'
            prefixo = 'ADB'
            cont_adb += 1
            num = cont_adb
        else:
            categoria = 'DIVERSOS'
            prefixo = 'DIV'
            num = 999 # Fallback
            
        codigo = f"{prefixo}-{num:04d}"
        
        # Verificar se já existe pelo nome para não duplicar
        produto, created = Produto.objects.get_or_create(
            nome=nome,
            defaults={
                'codigo': codigo,
                'categoria': categoria,
                'saldo': quantidade,
                'local': local,
                'minimo': 0
            }
        )
        
        if created:
            criados += 1
        else:
            # Se já existe, apenas somamos o saldo ou atualizamos
            produto.saldo = quantidade
            produto.categoria = categoria
            produto.local = local
            produto.save()
            atualizados += 1
            
    print(f"Importação concluída: {criados} novos produtos, {atualizados} atualizados.")

if __name__ == "__main__":
    importar()
