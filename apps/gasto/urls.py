from django.urls import path
from .views import page_gastos, crear_gasto

urlpatterns = [
    path('', page_gastos, name="page_gastos"),
    path('crear/', crear_gasto, name="crear_gasto"),
]