from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.menu, name='menu'),
    path('3ra_infantil/', views.tercera_infantil, name='3ra_infantil'),
    path('clubes/', views.clubes, name='clubes'),
    path('encargados_clubes/', views.encargados_clubes, name='encargados_clubes'),
    path('clubes/add/', views.clubes_add, name='clubes_add'),
    path('clubes/edit/<int:club_id>/', views.clubes_edit, name='clubes_edit'),
    path('clubes/delete/<int:club_id>/', views.clubes_delete, name='clubes_delete'),
    path('encargados_clubes/<int:club_id>/', views.encargado_edit, name='encargado_edit'),
    path('serie_honor/', views.serie_honor, name='serie_honor'),
    path('serie_femenino/', views.serie_femenino, name='serie_femenino'),
    path('serie_segunda_adultos/', views.serie_segunda_adultos, name='serie_segunda_adultos'),
    path('serie_seniors/', views.serie_seniors, name='serie_seniors'),
    path('serie_super_seniors/', views.serie_super_seniors, name='serie_super_seniors'),
    path('serie_segunda_infantil/', views.serie_segunda_infantil, name='serie_segunda_infantil'),
    path('serie_juvenil/', views.serie_juvenil, name='serie_juvenil'),
    path('serie_primera_infantil/', views.serie_primera_infantil, name='serie_primera_infantil'),
    path('serie_tercera_infantil/', views.serie_tercera_infantil, name='serie_tercera_infantil'),
]

