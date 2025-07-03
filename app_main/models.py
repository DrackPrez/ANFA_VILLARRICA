from django.db import models

# Create your models here.

class Clubes(models.Model):
    club = models.CharField(max_length=100, unique=True)
    super_seniors = models.BooleanField(default=False)
    seniors = models.BooleanField(default=False)
    honor = models.BooleanField(default=False)
    segunda_honor = models.BooleanField(default=False)
    juveniles = models.BooleanField(default=False)
    primera_infantil = models.BooleanField(default=False)
    segunda_infantil = models.BooleanField(default=False)
    tercera_infantil = models.BooleanField(default=False)
    femenino = models.BooleanField(default=False)

    def __str__(self):
        return self.club

class ValorArbitro(models.Model):
    serie = models.CharField(max_length=50, unique=True)
    medio_tiempo_min = models.PositiveSmallIntegerField()
    tiempo_completo_min = models.PositiveSmallIntegerField()
    tiempo_con_descanso = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=0)
    cantidad = models.CharField(max_length=10)

    def __str__(self):
        return self.serie

class EncargadoSerie(models.Model):
    club = models.OneToOneField('Clubes', on_delete=models.CASCADE, related_name='encargado')
    presidente = models.CharField(max_length=100, blank=True, default="")
    super_seniors = models.CharField(max_length=100, blank=True, default="")
    seniors = models.CharField(max_length=100, blank=True, default="")
    honor = models.CharField(max_length=100, blank=True, default="")
    segunda_honor = models.CharField(max_length=100, blank=True, default="")
    juveniles = models.CharField(max_length=100, blank=True, default="")
    primera_infantil = models.CharField(max_length=100, blank=True, default="")
    segunda_infantil = models.CharField(max_length=100, blank=True, default="")
    tercera_infantil = models.CharField(max_length=100, blank=True, default="")
    femenino = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.club} - Encargados de series"
