import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'

django.setup()

from almox.models import Produto

def limpar_categorias():
    produtos = Produto.objects.all()
    atualizados = 0
    
    for p in produtos:
        cat_antiga = p.categoria
        nova_cat = cat_antiga.upper().strip()
        
        # Padronizar nomes
        if nova_cat == 'FERRAMENTA':
            nova_cat = 'FERRAMENTAS'
        
        if cat_antiga != nova_cat:
            p.categoria = nova_cat
            p.save()
            atualizados += 1
            
    print(f"Limpeza concluída: {atualizados} produtos padronizados.")

if __name__ == "__main__":
    limpar_categorias()
