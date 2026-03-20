from django.urls import path
from .views import detalle_productos, page_ventas, registrar_venta, reporte_ventas_mensual, ver_ventas, reporte_ventas_diaria

urlpatterns = [
    path('', page_ventas, name="ventas"),
    path("registrar/", registrar_venta, name="registrar_venta"),
    path("ver/", ver_ventas, name="ver_ventas"),
    path("reporte/diario/", reporte_ventas_diaria, name="reporte_ventas_diaria"),
    path("reporte/mensual/", reporte_ventas_mensual, name="reporte_ventas_mensual"),
    path("detalle-productos/", detalle_productos, name="detalle_productos"),
]
