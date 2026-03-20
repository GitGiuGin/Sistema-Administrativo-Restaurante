from django.urls import path
from .views import crear, editar, form_usuario, usuarios, detalle_usuario, habilitar, inhabilitar, page_perfil, form_contraseña, cambiar_password, reset_password

urlpatterns = [
    path('', usuarios, name="page_usuario"),
    path('perfil/', page_perfil, name="page_perfil"),
    path('form/', form_usuario, name="form_usuario"),
    path('crear/', crear, name="crear_usuario"),
    path('editar/<str:token>/', editar, name="editar_usuario"),
    path('usuarios/detalle/', detalle_usuario, name="detalle_usuario"),
    path('habilitar/<int:usuario_id>/', habilitar, name="habilitar_usuario"),
    path('inhabilitar/<int:usuario_id>/', inhabilitar, name="inhabilitar_usuario"),
    path('form_contraseña/', form_contraseña, name="form_contraseña"),
    path('cambiar_password/', cambiar_password, name='cambiar_password'),
    path('cambiar_password/<int:user_id>/', reset_password, name='reset_password'),
]