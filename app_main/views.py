from django.shortcuts import render, redirect, get_object_or_404
from .models import Clubes, EncargadoSerie, SerieHonor, Fase, Jornada, Tablero_SerieHonor, SerieFemenino, Tablero_SerieFemenino, SerieSegundaAdultos, Tablero_SerieSegundaAdultos
# Agregar importación de SerieSeniors, Tablero_SerieSeniors, SerieSuperSeniors y Tablero_SerieSuperSeniors
from .models import SerieSeniors, Tablero_SerieSeniors, SerieSuperSeniors, Tablero_SerieSuperSeniors
from .models import SerieSegundaInfantil, Tablero_SerieSegundaInfantil
from .models import SerieJuvenil, Tablero_SerieJuvenil,SeriePrimeraInfantil,Tablero_SeriePrimeraInfantil
from .models import SerieTerceraInfantil, Tablero_SerieTerceraInfantil
from .models import Novedad, NovedadImagen
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from datetime import date, timedelta
from django.urls import reverse
from django.http import JsonResponse

def menu(request):
    hoy = date.today()
    proximos_partidos = []
    resultados_recientes = []

    # (modelo, nombre legible de la serie, nombre de la url de la serie)
    series = [
        (SerieHonor, "1ra Adultos Honor", 'serie_honor'),
        (SerieSegundaAdultos, "2da Adultos", 'serie_segunda_adultos'),
        (SerieSeniors, "Seniors", 'serie_seniors'),
        (SerieSuperSeniors, "Super Seniors", 'serie_super_seniors'),
        (SerieJuvenil, "Juvenil", 'serie_juvenil'),
        (SeriePrimeraInfantil, "Primera Infantil", 'serie_primera_infantil'),
        (SerieSegundaInfantil, "Segunda Infantil", 'serie_segunda_infantil'),
        (SerieTerceraInfantil, "Tercera Infantil", 'serie_tercera_infantil'),
        (SerieFemenino, "Femenino", 'serie_femenino'),
    ]

    for modelo, nombre_serie, url_name in series:
        # Próximos partidos
        for p in modelo.objects.filter(fecha__gte=hoy).order_by('fecha', 'horario'):
            # Acortar la fase a las primeras dos palabras
            fase_nombre = ''
            if p.jornada and p.jornada.fase and p.jornada.fase.nombre:
                fase_nombre = ' '.join(p.jornada.fase.nombre.split()[:2])
            proximos_partidos.append({
                'id': p.id,
                'fecha': p.fecha,
                'hora': p.horario if hasattr(p, 'horario') else getattr(p, 'hora', None),
                'serie': nombre_serie,
                'fase': fase_nombre,
                'jornada': p.jornada.nombre if p.jornada else '',
                'jornada_id': p.jornada.id if p.jornada else '',
                'equipo_local': p.equipo_local,
                'equipo_visita': p.equipo_visita,
                'cancha': p.cancha,
                'serie_url': reverse(url_name),
            })
        # Resultados recientes (partidos jugados de hoy a 5 días atrás, con resultado)
        for p in modelo.objects.filter(fecha__gte=hoy - timedelta(days=5), fecha__lte=hoy).order_by('-fecha', '-horario'):
            # Solo mostrar si tiene goles ingresados (ambos equipos)
            goles_local = getattr(p, 'goles_local', None)
            goles_visita = getattr(p, 'goles_visita', None)
            if goles_local is not None and goles_visita is not None and (goles_local != '' and goles_visita != ''):
                fase_nombre = ''
                if p.jornada and p.jornada.fase and p.jornada.fase.nombre:
                    fase_nombre = ' '.join(p.jornada.fase.nombre.split()[:2])
                resultados_recientes.append({
                    'id': p.id,
                    'fecha': p.fecha,
                    'hora': p.horario if hasattr(p, 'horario') else getattr(p, 'hora', None),
                    'serie': nombre_serie,
                    'fase': fase_nombre,
                    'jornada': p.jornada.nombre if p.jornada else '',
                    'jornada_id': p.jornada.id if p.jornada else '',
                    'equipo_local': p.equipo_local,
                    'equipo_visita': p.equipo_visita,
                    'goles_local': goles_local,
                    'goles_visita': goles_visita,
                    'cancha': p.cancha,
                    'serie_url': reverse(url_name),
                })

    proximos_partidos.sort(key=lambda x: (x['fecha'], x['hora'] or ''))
    resultados_recientes.sort(key=lambda x: (x['fecha'], x['hora'] or ''), reverse=True)
    
    # Obtener más novedades para el carrusel (mostrar hasta 10)
    novedades_recientes = Novedad.objects.filter(activo=True)[:10]
    
    return render(request, 'menu.html', {
        'proximos_partidos': proximos_partidos,
        'resultados_recientes': resultados_recientes,
        'novedades_recientes': novedades_recientes
    })


def tercera_infantil(request):
    return render(request, '3era_infantil')


def clubes(request):
    clubes = Clubes.objects.all()
    return render(request, 'clubes.html', {'clubes': clubes})

@csrf_exempt  # Add this decorator for testing only!
@login_required
def clubes_add(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        club = Clubes(
            club=nombre,
            super_seniors=bool(request.POST.get('super_seniors')),
            seniors=bool(request.POST.get('seniors')),
            honor=bool(request.POST.get('honor')),
            segunda_honor=bool(request.POST.get('segunda_honor')),
            juveniles=bool(request.POST.get('juveniles')),
            primera_infantil=bool(request.POST.get('primera_infantil')),
            segunda_infantil=bool(request.POST.get('segunda_infantil')),
            tercera_infantil=bool(request.POST.get('tercera_infantil')),
            femenino=bool(request.POST.get('femenino')),
        )
        club.save()
        # Crear registro en EncargadoSerie com valores em branco
        EncargadoSerie.objects.create(club=club)
        return redirect('clubes')
    return redirect('clubes')

@login_required
def clubes_edit(request, club_id):
    club = get_object_or_404(Clubes, id=club_id)
    if request.method == 'POST':
        club.club = request.POST.get('nombre')
        club.super_seniors = bool(request.POST.get('super_seniors'))
        club.seniors = bool(request.POST.get('seniors'))
        club.honor = bool(request.POST.get('honor'))
        club.segunda_honor = bool(request.POST.get('segunda_honor'))
        club.juveniles = bool(request.POST.get('juveniles'))
        club.primera_infantil = bool(request.POST.get('primera_infantil'))
        club.segunda_infantil = bool(request.POST.get('segunda_infantil'))
        club.tercera_infantil = bool(request.POST.get('tercera_infantil'))
        club.femenino = bool(request.POST.get('femenino'))
        club.save()
        return redirect('clubes')
    return render(request, 'clubes_form.html', {'club': club})

@login_required
def clubes_delete(request, club_id):
    club = get_object_or_404(Clubes, id=club_id)
    if request.method == 'POST':
        club.delete()
        return redirect('clubes')
    return render(request, 'clubes_confirm_delete.html', {'club': club})


def encargados_clubes(request):
    clubes = Clubes.objects.all().select_related('encargado')
    return render(request, 'encargados_clubes.html', {'clubes': clubes})

@login_required
def encargado_edit(request, club_id):
    club = get_object_or_404(Clubes, id=club_id)
    encargado = getattr(club, 'encargado', None)
    if request.method == 'POST':
        if not encargado:
            encargado = EncargadoSerie(club=club)
        encargado.presidente = request.POST.get('presidente', '')
        encargado.super_seniors = request.POST.get('super_seniors', '')
        encargado.seniors = request.POST.get('seniors', '')
        encargado.honor = request.POST.get('honor', '')
        encargado.segunda_honor = request.POST.get('segunda_honor', '')
        encargado.juveniles = request.POST.get('juveniles', '')
        encargado.primera_infantil = request.POST.get('primera_infantil', '')
        encargado.segunda_infantil = request.POST.get('segunda_infantil', '')
        encargado.tercera_infantil = request.POST.get('tercera_infantil', '')
        encargado.femenino = request.POST.get('femenino', '')
        encargado.save()
        return redirect('encargados_clubes')
    return redirect('encargados_clubes')

def actualizar_tabla_posiciones(fase):
    # Obtener todos los equipos que participan en la fase
    equipos_local = SerieHonor.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieHonor.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    
    # Actualizar o crear registros de tabla para cada equipo
    for equipo in equipos:
        tablero, created = Tablero_SerieHonor.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general():
    # Diccionario para acumular estadísticas por equipo
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieHonor.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
        # Diferencia de goles se recalcula al final

    # Calcular DG y ordenar
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']

    # Ordenar por Pts, DG, GF
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_honor(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            # Solo fases de honor:
            fases = Fase.objects.filter(nombre__icontains="HONOR").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10  # Limita a décima
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 HONOR"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_honor')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_honor')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_honor')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_honor')
        elif 'add_row_modal' in request.POST:
            partido = SerieHonor.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',  # Estado vacío por defecto
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones(partido.jornada.fase)
            return redirect('serie_honor')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieHonor.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieHonor.objects.filter(id=row_id).delete()
            # Actualizar tabla después de eliminar partido
            if fase:
                actualizar_tabla_posiciones(fase)
            return redirect('serie_honor')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieHonor.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            # Asegura goles válidos
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones(partido.jornada.fase)
            return redirect('serie_honor')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieHonor.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        # Manejo seguro de goles
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieHonor.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones(fase)
            return redirect('serie_honor')
    fases = Fase.objects.filter(nombre__icontains="HONOR").prefetch_related('jornadas__partidos')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general()
    return render(request, 'serie_honor.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieHonor.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_femenino(fase):
    equipos_local = SerieFemenino.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieFemenino.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieFemenino.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_femenino():
    from collections import defaultdict
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieFemenino.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_femenino(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            # Solo fases de femenino:
            fases = Fase.objects.filter(nombre__icontains="FEMENINO").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 FEMENINO"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_femenino')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_femenino')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_femenino')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_femenino')
        elif 'add_row_modal' in request.POST:
            partido = SerieFemenino.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_femenino(partido.jornada.fase)
            return redirect('serie_femenino')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieFemenino.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieFemenino.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_femenino(fase)
            return redirect('serie_femenino')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieFemenino.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_femenino(partido.jornada.fase)
            return redirect('serie_femenino')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieFemenino.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieFemenino.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_femenino(fase)
            return redirect('serie_femenino')
    fases = Fase.objects.filter(nombre__icontains="FEMENINO").prefetch_related('jornadas__partidos_femenino')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_femenino()
    return render(request, 'serie_femenino.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieFemenino.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_segunda_adultos(fase):
    equipos_local = SerieSegundaAdultos.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieSegundaAdultos.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieSegundaAdultos.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_segunda_adultos():
    from collections import defaultdict
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieSegundaAdultos.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_segunda_adultos(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            # Solo fases de segunda adultos:
            fases = Fase.objects.filter(nombre__icontains="SEGUNDA ADULTOS").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 SEGUNDA ADULTOS"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_segunda_adultos')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_segunda_adultos')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_segunda_adultos')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_segunda_adultos')
        elif 'add_row_modal' in request.POST:
            partido = SerieSegundaAdultos.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_segunda_adultos(partido.jornada.fase)
            return redirect('serie_segunda_adultos')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieSegundaAdultos.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieSegundaAdultos.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_segunda_adultos(fase)
            return redirect('serie_segunda_adultos')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieSegundaAdultos.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_segunda_adultos(partido.jornada.fase)
            return redirect('serie_segunda_adultos')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieSegundaAdultos.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieSegundaAdultos.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_segunda_adultos(fase)
            return redirect('serie_segunda_adultos')
    fases = Fase.objects.filter(nombre__icontains="SEGUNDA ADULTOS").prefetch_related('jornadas__partidos_segunda_adultos')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_segunda_adultos()
    return render(request, 'serie_segunda_adultos.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieSegundaAdultos.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_seniors(fase):
    equipos_local = SerieSeniors.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieSeniors.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieSeniors.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_seniors():
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieSeniors.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_seniors(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            # Solo fases de seniors (no incluir super seniors)
            fases = Fase.objects.filter(nombre__icontains="SENIORS").exclude(nombre__icontains="SUPER").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 SENIORS"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_seniors')
        elif 'delete_fase' in request.POST:
            # Eliminar solo la fase seleccionada
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_seniors')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_seniors')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_seniors')
        elif 'add_row_modal' in request.POST:
            partido = SerieSeniors.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_seniors(partido.jornada.fase)
            return redirect('serie_seniors')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieSeniors.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieSeniors.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_seniors(fase)
            return redirect('serie_seniors')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieSeniors.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_seniors(partido.jornada.fase)
            return redirect('serie_seniors')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieSeniors.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieSeniors.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_seniors(fase)
            return redirect('serie_seniors')
    fases = Fase.objects.filter(nombre__icontains="SENIORS").exclude(nombre__icontains="SUPER").prefetch_related('jornadas__partidos_seniors')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_seniors()
    return render(request, 'serie_seniors.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieSeniors.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_super_seniors(fase):
    equipos_local = SerieSuperSeniors.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieSuperSeniors.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieSuperSeniors.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_super_seniors():
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieSuperSeniors.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_super_seniors(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            # Solo fases de super seniors
            fases = Fase.objects.filter(nombre__icontains="SUPER SENIORS").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 SUPER SENIORS"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_super_seniors')
        elif 'delete_fase' in request.POST:
            # Eliminar solo la fase seleccionada
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_super_seniors')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_super_seniors')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_super_seniors')
        elif 'add_row_modal' in request.POST:
            partido = SerieSuperSeniors.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_super_seniors(partido.jornada.fase)
            return redirect('serie_super_seniors')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieSuperSeniors.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieSuperSeniors.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_super_seniors(fase)
            return redirect('serie_super_seniors')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieSuperSeniors.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_super_seniors(partido.jornada.fase)
            return redirect('serie_super_seniors')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieSuperSeniors.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieSuperSeniors.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_super_seniors(fase)
            return redirect('serie_super_seniors')
    fases = Fase.objects.filter(nombre__icontains="SUPER SENIORS").prefetch_related('jornadas__partidos_super_seniors')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_super_seniors()
    return render(request, 'serie_super_seniors.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieSuperSeniors.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_segunda_infantil(fase):
    equipos_local = SerieSegundaInfantil.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieSegundaInfantil.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieSegundaInfantil.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_segunda_infantil():
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieSegundaInfantil.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_segunda_infantil(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            fases = Fase.objects.filter(nombre__icontains="SEGUNDA INFANTIL").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 SEGUNDA INFANTIL"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_segunda_infantil')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_segunda_infantil')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_segunda_infantil')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_segunda_infantil')
        elif 'add_row_modal' in request.POST:
            partido = SerieSegundaInfantil.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_segunda_infantil(partido.jornada.fase)
            return redirect('serie_segunda_infantil')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieSegundaInfantil.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieSegundaInfantil.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_segunda_infantil(fase)
            return redirect('serie_segunda_infantil')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieSegundaInfantil.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            # Asegura goles válidos
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_segunda_infantil(partido.jornada.fase)
            return redirect('serie_segunda_infantil')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieSegundaInfantil.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieSegundaInfantil.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_segunda_infantil(fase)
            return redirect('serie_segunda_infantil')
    fases = Fase.objects.filter(nombre__icontains="SEGUNDA INFANTIL").prefetch_related('jornadas__partidos_segunda_infantil')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_segunda_infantil()
    return render(request, 'serie_segunda_infantil.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieSegundaInfantil.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_juvenil(fase):
    equipos_local = SerieJuvenil.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieJuvenil.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieJuvenil.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_juvenil():
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieJuvenil.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_juvenil(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            fases = Fase.objects.filter(nombre__icontains="JUVENIL").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 JUVENIL"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_juvenil')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_juvenil')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_juvenil')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_juvenil')
        elif 'add_row_modal' in request.POST:
            partido = SerieJuvenil.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_juvenil(partido.jornada.fase)
            return redirect('serie_juvenil')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieJuvenil.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieJuvenil.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_juvenil(fase)
            return redirect('serie_juvenil')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieJuvenil.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_juvenil(partido.jornada.fase)
            return redirect('serie_juvenil')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieJuvenil.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieJuvenil.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_juvenil(fase)
            return redirect('serie_juvenil')
    fases = Fase.objects.filter(nombre__icontains="JUVENIL").prefetch_related('jornadas__partidos_juvenil')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_juvenil()
    return render(request, 'serie_juvenil.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieJuvenil.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

############################

def actualizar_tabla_posiciones_primera_infantil(fase):
    equipos_local = SeriePrimeraInfantil.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SeriePrimeraInfantil.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SeriePrimeraInfantil.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_primera_infantil():
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SeriePrimeraInfantil.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_primera_infantil(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            fases = Fase.objects.filter(nombre__icontains="PRIMERA INFANTIL").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"

            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 PRIMERA INFANTIL"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_primera_infantil')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_primera_infantil')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_primera_infantil')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_primera_infantil')
        elif 'add_row_modal' in request.POST:
            partido = SeriePrimeraInfantil.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_primera_infantil(partido.jornada.fase)
            return redirect('serie_primera_infantil')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SeriePrimeraInfantil.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SeriePrimeraInfantil.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_primera_infantil(fase)
            return redirect('serie_primera_infantil')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SeriePrimeraInfantil.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_primera_infantil(partido.jornada.fase)
            return redirect('serie_primera_infantil')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SeriePrimeraInfantil.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SeriePrimeraInfantil.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_primera_infantil(fase)
            return redirect('serie_primera_infantil')
    fases = Fase.objects.filter(nombre__icontains="PRIMERA INFANTIL").prefetch_related('jornadas__partidos_primera_infantil')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_primera_infantil()
    return render(request, 'serie_primera_infantil.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SeriePrimeraInfantil.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

def actualizar_tabla_posiciones_tercera_infantil(fase):
    equipos_local = SerieTerceraInfantil.objects.filter(jornada__fase=fase).values_list('equipo_local', flat=True).distinct()
    equipos_visita = SerieTerceraInfantil.objects.filter(jornada__fase=fase).values_list('equipo_visita', flat=True).distinct()
    equipos = Clubes.objects.filter(id__in=set(list(equipos_local) + list(equipos_visita)))
    for equipo in equipos:
        tablero, created = Tablero_SerieTerceraInfantil.objects.get_or_create(
            fase=fase,
            equipo=equipo
        )
        tablero.actualizar_estadisticas()

def calcular_tablero_general_tercera_infantil():
    stats = defaultdict(lambda: {
        'equipo': None, 'PJ': 0, 'PG': 0, 'PE': 0, 'PP': 0, 'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
    })
    for tablero in Tablero_SerieTerceraInfantil.objects.all():
        equipo_id = tablero.equipo.id
        stats[equipo_id]['equipo'] = tablero.equipo
        stats[equipo_id]['PJ'] += tablero.PJ
        stats[equipo_id]['PG'] += tablero.PG
        stats[equipo_id]['PE'] += tablero.PE
        stats[equipo_id]['PP'] += tablero.PP
        stats[equipo_id]['GF'] += tablero.GF
        stats[equipo_id]['GC'] += tablero.GC
        stats[equipo_id]['Pts'] += tablero.Pts
    for equipo_id in stats:
        stats[equipo_id]['DG'] = stats[equipo_id]['GF'] - stats[equipo_id]['GC']
    clasificacion = sorted(
        stats.values(),
        key=lambda x: (x['Pts'], x['DG'], x['GF']),
        reverse=True
    )
    return clasificacion


def serie_tercera_infantil(request):
    if request.method == 'POST':
        if 'add_fase' in request.POST:
            ordinales = [
                "PRIMERA", "SEGUNDA", "TERCERA", "CUARTA", "QUINTA",
                "SEXTA", "SÉPTIMA", "OCTAVA", "NOVENA", "DÉCIMA"
            ]
            fases = Fase.objects.filter(nombre__icontains="TERCERA INFANTIL").order_by('id')
            next_num = fases.count() + 1
            if next_num > 10:
                next_num = 10
            nombre_ordinal = ordinales[next_num - 1] if next_num <= 10 else f"{next_num}ª"
            nombre_fase = f"{nombre_ordinal} RUEDA - APERTURA CAMPEONATO DEMARCA SPORT ANFA 2025 TERCERA INFANTIL"
            if not Fase.objects.filter(nombre=nombre_fase).exists():
                Fase.objects.create(nombre=nombre_fase)
            return redirect('serie_tercera_infantil')
        elif 'delete_fase' in request.POST:
            Fase.objects.filter(id=request.POST.get('delete_fase')).delete()
            return redirect('serie_tercera_infantil')
        elif 'add_jornada' in request.POST:
            fase_id = request.POST.get('fase_id')
            jornadas = Jornada.objects.filter(fase_id=fase_id).order_by('id')
            next_num = jornadas.count() + 1
            nombre_jornada = f"Jornada {next_num}"
            Jornada.objects.create(fase_id=fase_id, nombre=nombre_jornada)
            return redirect('serie_tercera_infantil')
        elif 'delete_jornada' in request.POST:
            Jornada.objects.filter(id=request.POST.get('delete_jornada')).delete()
            return redirect('serie_tercera_infantil')
        elif 'add_row_modal' in request.POST:
            partido = SerieTerceraInfantil.objects.create(
                jornada_id=request.POST.get('modal_jornada'),
                equipo_local_id=request.POST.get('modal_equipo_local'),
                estado_partido_local='',
                goles_local=0,
                goles_visita=0,
                estado_partido_visita='',
                equipo_visita_id=request.POST.get('modal_equipo_visita'),
                horario=request.POST.get('modal_horario') or None,
                fecha=request.POST.get('modal_fecha') or None,
                cancha=request.POST.get('modal_cancha', ''),
                turno=request.POST.get('modal_turno', ''),
                libre=request.POST.get('modal_libre', ''),
            )
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_tercera_infantil(partido.jornada.fase)
            return redirect('serie_tercera_infantil')
        elif 'delete_row' in request.POST:
            row_id = request.POST.get('delete_row')
            partido = SerieTerceraInfantil.objects.filter(id=row_id).first()
            fase = partido.jornada.fase if partido else None
            SerieTerceraInfantil.objects.filter(id=row_id).delete()
            if fase:
                actualizar_tabla_posiciones_tercera_infantil(fase)
            return redirect('serie_tercera_infantil')
        elif 'edit_row_modal' in request.POST:
            partido_id = request.POST.get('edit_partido_id')
            partido = SerieTerceraInfantil.objects.get(id=partido_id)
            partido.equipo_local_id = request.POST.get('edit_equipo_local')
            partido.equipo_visita_id = request.POST.get('edit_equipo_visita')
            partido.horario = request.POST.get('edit_horario') or None
            partido.fecha = request.POST.get('edit_fecha') or None
            partido.cancha = request.POST.get('edit_cancha', '')
            partido.turno = request.POST.get('edit_turno', '')
            partido.libre = request.POST.get('edit_libre', '')
            goles_local = request.POST.get('goles_local_{}'.format(partido_id), partido.goles_local)
            goles_visita = request.POST.get('goles_visita_{}'.format(partido_id), partido.goles_visita)
            partido.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
            partido.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
            partido.actualizar_estados()
            partido.save()
            actualizar_tabla_posiciones_tercera_infantil(partido.jornada.fase)
            return redirect('serie_tercera_infantil')
        else:
            fase_ids_actualizadas = set()
            for key in request.POST:
                if key.startswith('id_'):
                    row_id = key.split('_')[1]
                    try:
                        sh = SerieTerceraInfantil.objects.get(id=row_id)
                        sh.jornada_id = request.POST.get(f'jornada_{row_id}', sh.jornada_id)
                        sh.equipo_local_id = request.POST.get(f'equipo_local_{row_id}', sh.equipo_local_id)
                        goles_local = request.POST.get(f'goles_local_{row_id}', sh.goles_local)
                        goles_visita = request.POST.get(f'goles_visita_{row_id}', sh.goles_visita)
                        sh.goles_local = int(goles_local) if str(goles_local).isdigit() else 0
                        sh.goles_visita = int(goles_visita) if str(goles_visita).isdigit() else 0
                        sh.equipo_visita_id = request.POST.get(f'equipo_visita_{row_id}', sh.equipo_visita_id)
                        sh.horario = request.POST.get(f'horario_{row_id}', sh.horario) or None
                        sh.fecha = request.POST.get(f'fecha_{row_id}', sh.fecha) or None
                        sh.cancha = request.POST.get(f'cancha_{row_id}', sh.cancha)
                        sh.turno = request.POST.get(f'turno_{row_id}', sh.turno)
                        sh.libre = request.POST.get(f'libre_{row_id}', sh.libre)
                        sh.actualizar_estados()
                        sh.save()
                        fase_ids_actualizadas.add(sh.jornada.fase_id)
                    except SerieTerceraInfantil.DoesNotExist:
                        continue
            # Actualizar tabla después de actualizar goles/partidos
            for fase_id in fase_ids_actualizadas:
                fase = Fase.objects.get(id=fase_id)
                actualizar_tabla_posiciones_tercera_infantil(fase)
            return redirect('serie_tercera_infantil')
    fases = Fase.objects.filter(nombre__icontains="TERCERA INFANTIL").prefetch_related('jornadas__partidos_tercera_infantil')
    clubes = Clubes.objects.all()
    jornadas = Jornada.objects.all()
    tablero_general = calcular_tablero_general_tercera_infantil()
    return render(request, 'serie_tercera_infantil.html', {
        'fases': fases,
        'clubes': clubes,
        'jornadas': jornadas,
        'estado_choices': SerieTerceraInfantil.ESTADO_PARTIDO_CHOICES,
        'tablero_general': tablero_general,
    })

# --- NUEVAS VISTAS PARA NOVEDADES ---

def novedades(request):
    novedades = Novedad.objects.filter(activo=True).prefetch_related('imagenes').order_by('-fecha_creacion')
    return render(request, 'novedades.html', {'novedades': novedades})

@login_required
def novedad_add(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        url_instagram = request.POST.get('url_instagram', '')
        
        # Crear la novedad
        novedad = Novedad.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            url_instagram=url_instagram
        )
        
        # Manejar múltiples imágenes
        imagenes = request.FILES.getlist('imagenes')
        if imagenes:
            for i, imagen in enumerate(imagenes[:5]):  # Limitar a 5 imágenes
                NovedadImagen.objects.create(
                    novedad=novedad,
                    imagen=imagen,
                    orden=i
                )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Novedad agregada exitosamente'})
        return redirect('menu')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    return redirect('menu')

@login_required
def novedad_edit(request, novedad_id):
    novedad = get_object_or_404(Novedad, id=novedad_id)
    
    if request.method == 'POST':
        novedad.titulo = request.POST.get('titulo', novedad.titulo)
        novedad.descripcion = request.POST.get('descripcion', novedad.descripcion)
        novedad.url_instagram = request.POST.get('url_instagram', '')
        novedad.save()
        
        # Manejar nuevas imágenes
        imagenes = request.FILES.getlist('imagenes')
        if imagenes:
            # Eliminar imágenes existentes (incluyendo archivos físicos)
            for img in novedad.imagenes.all():
                if img.imagen and img.imagen.name:
                    try:
                        import os
                        if os.path.isfile(img.imagen.path):
                            os.remove(img.imagen.path)
                    except Exception as e:
                        print(f"Error al eliminar archivo {img.imagen.path}: {e}")
                img.delete()
            # Crear nuevas imágenes
            for i, imagen in enumerate(imagenes[:5]):  # Limitar a 5 imágenes
                NovedadImagen.objects.create(
                    novedad=novedad,
                    imagen=imagen,
                    orden=i
                )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Novedad actualizada exitosamente'})
        return redirect('menu')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        imagenes_urls = [img.imagen.url for img in novedad.imagenes.all()]
        return JsonResponse({
            'novedad': {
                'id': novedad.id,
                'titulo': novedad.titulo,
                'descripcion': novedad.descripcion,
                'url_instagram': novedad.url_instagram or '',
                'imagenes_urls': imagenes_urls
            }
        })
    return redirect('menu')

@login_required
def novedad_delete(request, novedad_id):
    novedad = get_object_or_404(Novedad, id=novedad_id)
    
    if request.method == 'POST':
        # Eliminar las imágenes físicas del servidor antes de eliminar la novedad
        for imagen in novedad.imagenes.all():
            if imagen.imagen and imagen.imagen.name:
                # Eliminar el archivo físico del sistema
                try:
                    import os
                    if os.path.isfile(imagen.imagen.path):
                        os.remove(imagen.imagen.path)
                except Exception as e:
                    # Si hay error al eliminar el archivo, continuar con la eliminación lógica
                    print(f"Error al eliminar archivo {imagen.imagen.path}: {e}")
        
        # Marcar la novedad como inactiva (eliminación lógica)
        novedad.activo = False
        novedad.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Novedad eliminada exitosamente'})
        return redirect('menu')
    
    return redirect('menu')
