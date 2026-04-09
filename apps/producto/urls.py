from django.urls import path
from .views import page_productos, crear, editar, habilitar, inhabilitar, buscar

urlpatterns = [
    path('', page_productos, name="productos"),
    path('crear/', crear, name="crear_producto"),
    path('editar/<int:producto_id>/', editar, name="editar_producto"),
    path('habilitar/<int:producto_id>/', habilitar, name="habilitar_producto"),
    path('inhabilitar/<int:producto_id>/', inhabilitar, name="inhabilitar_producto"),
    path("buscar/", buscar, name="buscar_productos"),
]
