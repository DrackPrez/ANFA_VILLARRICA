from django.shortcuts import render, redirect, get_object_or_404
from .models import Clubes, EncargadoSerie
from django.views.decorators.csrf import csrf_exempt

def menu(request):
    return render(request, 'menu.html')

def tercera_infantil(request):
    return render(request, '3era_infantil')

def clubes(request):
    clubes = Clubes.objects.all()
    return render(request, 'clubes.html', {'clubes': clubes})

@csrf_exempt  # Add this decorator for testing only!
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
        # Crear registro en EncargadoSerie con valores en blanco
        EncargadoSerie.objects.create(club=club)
        return redirect('clubes')
    return redirect('clubes')

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

def clubes_delete(request, club_id):
    club = get_object_or_404(Clubes, id=club_id)
    if request.method == 'POST':
        club.delete()
        return redirect('clubes')
    return render(request, 'clubes_confirm_delete.html', {'club': club})

def encargados_clubes(request):
    clubes = Clubes.objects.all().select_related('encargado')
    return render(request, 'encargados_clubes.html', {'clubes': clubes})

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
