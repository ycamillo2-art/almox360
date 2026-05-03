from django.db import models
from django.contrib.auth.models import User

class Produto(models.Model):
    CATEGORIAS = [
        ('DIVERSOS', 'DIVERSOS'),
        ('FERRAMENTAS', 'FERRAMENTAS'),
        ('DEFENSIVOS', 'DEFENSIVOS'),
        ('ADUBO', 'ADUBO'),
    ]
    
    LOCAIS = [
        ('ALMOX 1', 'ALMOX 1'),
        ('ALMOX 2', 'ALMOX 2'),
        ('ALMOX 3', 'ALMOX 3'),
        ('ALMOX 4', 'ALMOX 4'),
        ('ALMOX 5', 'ALMOX 5'),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='DIVERSOS')
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    local = models.CharField(max_length=50, choices=LOCAIS, default='ALMOX 1')
    minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observacao = models.TextField(blank=True, null=True)
    em_uso = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class Historico(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    produto_info = models.CharField(max_length=255) # Armazena como texto para histórico permanente
    tipo = models.CharField(max_length=50) # Categoria ou Tipo de Movimentação
    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    responsavel = models.CharField(max_length=100)
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2)
    local = models.CharField(max_length=50)
    devolvido = models.CharField(max_length=10, default='NÃO') # SIM/NÃO/NA

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.data.strftime('%d/%m/%Y')} - {self.produto_info}"
