from django.urls import path
from .views import caja, abrir_caja, cerrar_caja, ver_turnos, crear_egreso

urlpatterns = [
    path('', caja, name='ver_caja'),
    path('turno/<int:turno_id>/', caja, name='ver_caja_turno'),
    path('abrir-turno/', abrir_caja, name='abrir_caja'),
    path('cerrar-turno/', cerrar_caja, name='cerrar_caja'),
    path('ver-turnos/', ver_turnos, name='ver_turnos'),
    path('crear_egreso/', crear_egreso, name="crear_egreso")
]
