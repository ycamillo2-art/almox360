import os
import sys
import django
from django.db.models import Count

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'

django.setup()

from almox.models import Produto

print(f"Total no Banco: {Produto.objects.count()}")
stats = Produto.objects.values('categoria').annotate(total=Count('id'))
for s in stats:
    print(f"Categoria: {s['categoria']} | Total: {s['total']}")
