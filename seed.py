import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'almox360_root.settings')
django.setup()

from django.contrib.auth.models import User
from almox.models import Produto

# Create Superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin / admin123")

# Create initial data
if Produto.objects.count() == 0:
    Produto.objects.create(codigo='FER-0001', nome='Pá de Bico', categoria='FERRAMENTAS', saldo=10, minimo=2, local='ALMOX 1')
    Produto.objects.create(codigo='DEF-0001', nome='Glifosato 1L', categoria='DEFENSIVOS', saldo=50, minimo=10, local='ALMOX 2')
    print("Initial products created.")
