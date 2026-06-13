import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'

django.setup()

from almox.models import Produto

print(f"Total no Banco (Postgres): {Produto.objects.count()}")
print(f"Defensivos: {Produto.objects.filter(categoria='DEFENSIVOS').count()}")
print(f"Adubo: {Produto.objects.filter(categoria='ADUBO').count()}")
print(f"Diversos: {Produto.objects.filter(categoria='DIVERSOS').count()}")
print(f"Ferramentas: {Produto.objects.filter(categoria='FERRAMENTAS').count()}")
