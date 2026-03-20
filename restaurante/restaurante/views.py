from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.venta.services import calcular_totales
from apps.venta.selectors import listar_ventas_dia
from apps.caja.selectors import obtener_turno_abierto
from apps.caja.services import movimientos_caja

@login_required
def inicio(request):
    ventas = listar_ventas_dia()
    total_general, total_costos, total_ganancia = calcular_totales(ventas)

    context = {
        "ventas": ventas,
        "total_general": total_general,
        "total_costos": total_costos,
        "total_ganancia": total_ganancia,
    }

    if request.user.groups.filter(name="Cajero").exists():
        turno = obtener_turno_abierto(request.user)
        movimientos = movimientos_caja(request, tipo="INGRESO")

        context = {
            "turno": turno,
            "movimientos": movimientos
        }
        
        return render(request, "pages/home.html", context)

    return render(request, "pages/dashboard.html", context)