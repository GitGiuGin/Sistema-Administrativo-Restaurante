from django.urls import path
from .views import page_categoria, crear, habilitar, inhabilitar, toggle_ver_en_ventas_view

urlpatterns = [
    path('', page_categoria, name="categorias"),
    path('crear/', crear, name="crear_categoria"),
    path('habilitar/<int:categoria_id>/', habilitar, name="habilitar_categoria"),
    path('inhabilitar/<int:categoria_id>/', inhabilitar, name="inhabilitar_categoria"),
    path("toggle-ver-en-ventas/", toggle_ver_en_ventas_view, name="toggle_ver_en_ventas"),
]
