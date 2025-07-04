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

class Fase(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Jornada(models.Model):
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='jornadas')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.fase} - {self.nombre}"

class SerieHonor(models.Model):
    ESTADO_PARTIDO_CHOICES = [
        ('PARTIDO GANADO', 'PARTIDO GANADO'),
        ('PARTIDO EMPATADO', 'PARTIDO EMPATADO'),
        ('PARTIDO PERDIDO', 'PARTIDO PERDIDO'),
    ]

    jornada = models.ForeignKey(Jornada, on_delete=models.CASCADE, related_name='partidos')
    equipo_local = models.ForeignKey('Clubes', on_delete=models.CASCADE, related_name='partidos_local')
    estado_partido_local = models.CharField(max_length=50, choices=ESTADO_PARTIDO_CHOICES)
    goles_local = models.PositiveSmallIntegerField()
    goles_visita = models.PositiveSmallIntegerField()
    estado_partido_visita = models.CharField(max_length=50, choices=ESTADO_PARTIDO_CHOICES)
    equipo_visita = models.ForeignKey('Clubes', on_delete=models.CASCADE, related_name='partidos_visita')
    horario = models.TimeField(null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)
    cancha = models.CharField(max_length=100, blank=True, default="")
    turno = models.CharField(max_length=50)
    libre = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.jornada}: {self.equipo_local} vs {self.equipo_visita}"

    def partido_agendado(self):
        return self.fecha and self.horario and self.cancha

    def actualizar_estados(self):
        if not self.partido_agendado():
            self.estado_partido_local = ""
            self.estado_partido_visita = ""
        else:
            if self.goles_local > self.goles_visita:
                self.estado_partido_local = 'PARTIDO GANADO'
                self.estado_partido_visita = 'PARTIDO PERDIDO'
            elif self.goles_local < self.goles_visita:
                self.estado_partido_local = 'PARTIDO PERDIDO'
                self.estado_partido_visita = 'PARTIDO GANADO'
            else:
                self.estado_partido_local = 'PARTIDO EMPATADO'
                self.estado_partido_visita = 'PARTIDO EMPATADO'

class Tablero_SerieHonor(models.Model):
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name='tableros')
    equipo = models.ForeignKey(Clubes, on_delete=models.CASCADE)
    PJ = models.IntegerField(default=0)
    PG = models.IntegerField(default=0)
    PE = models.IntegerField(default=0)
    PP = models.IntegerField(default=0)
    GF = models.IntegerField(default=0)
    GC = models.IntegerField(default=0)
    DG = models.IntegerField(default=0)
    Pts = models.IntegerField(default=0)

    class Meta:
        ordering = ['-Pts', '-DG', '-GF']
        unique_together = ['fase', 'equipo']

    def __str__(self):
        return f"{self.fase} - {self.equipo}"

    def actualizar_estadisticas(self):
        partidos_local = SerieHonor.objects.filter(
            jornada__fase=self.fase,
            equipo_local=self.equipo
        )
        partidos_visita = SerieHonor.objects.filter(
            jornada__fase=self.fase,
            equipo_visita=self.equipo
        )

        self.PJ = 0
        self.PG = 0
        self.PE = 0
        self.PP = 0
        self.GF = 0
        self.GC = 0

        # Solo cuentan los partidos agendados (fecha, hora y cancha)
        for partido in partidos_local:
            if partido.partido_agendado():
                self.PJ += 1
                self.GF += partido.goles_local
                self.GC += partido.goles_visita
                if partido.goles_local > partido.goles_visita:
                    self.PG += 1
                elif partido.goles_local < partido.goles_visita:
                    self.PP += 1
                else:
                    self.PE += 1

        for partido in partidos_visita:
            if partido.partido_agendado():
                self.PJ += 1
                self.GF += partido.goles_visita
                self.GC += partido.goles_local
                if partido.goles_visita > partido.goles_local:
                    self.PG += 1
                elif partido.goles_visita < partido.goles_local:
                    self.PP += 1
                else:
                    self.PE += 1

        self.DG = self.GF - self.GC
        self.Pts = (self.PG * 3) + self.PE
        self.save()


