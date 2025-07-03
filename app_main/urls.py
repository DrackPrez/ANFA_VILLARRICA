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
]

