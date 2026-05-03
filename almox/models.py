from django.db import models

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
    produto_info = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50)
    quantidade = models.DecimalField(max_digits=12, decimal_places=2)
    responsavel = models.CharField(max_length=100)
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_atual = models.DecimalField(max_digits=12, decimal_places=2)
    local = models.CharField(max_length=50)
    devolvido = models.CharField(max_length=10, default='NÃO')

    class Meta:
        ordering = ['-data']

class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    descricao = models.CharField(max_length=200)
    km_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.placa} - {self.descricao}"

class Abastecimento(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    combustivel = models.CharField(max_length=50)
    litros = models.DecimalField(max_digits=10, decimal_places=2)
    km_no_abastecimento = models.DecimalField(max_digits=12, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class Manutencao(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    descricao = models.TextField()
    custo = models.DecimalField(max_digits=12, decimal_places=2)
    km_da_manutencao = models.DecimalField(max_digits=12, decimal_places=2)
