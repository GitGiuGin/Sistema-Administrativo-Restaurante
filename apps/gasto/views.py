from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from apps.caja.services import movimientos_caja
from apps.caja.selectors import turnos_abiertos_operativo
from apps.gasto.services import crear, listar, listar_categorias

from apps.caja.models import TurnoCaja

@login_required
def page_gastos(request):
    tab = request.GET.get("tab", "operativos")
    fecha = request.GET.get("fecha")
            
    context = {
        "movimientos": movimientos_caja(request, fecha=fecha, tipo="EGRESO"),
        "turnos": turnos_abiertos_operativo(),
        "gastos": listar(fecha=fecha),
        "categorias_gastos": listar_categorias(),
        "current_tab": tab,
    }
    return render(request, "gasto/page_gastos.html", context)

@login_required
def crear_gasto(request):
    if request.method == "POST":
        data = {
            "categoria": request.POST.get("categoria"),
            "monto": Decimal(request.POST.get("monto")),
            "concepto": request.POST.get("concepto"),
            "descripcion": request.POST.get("descripcion"),
            "usuario": request.user,
        }
        try:
            crear(data)
            messages.success(request, "Gasto registrado correctamente")
        except ValidationError as e:
            messages.error(request, e.message_dict)

    return redirect("page_gastos")