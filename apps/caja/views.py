from urllib import request
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from apps.caja.services import abrir, cerrar, movimientos_caja, obtener_turno_abierto, registrar_egreso
from apps.caja.selectors import arqueos_caja
from apps.caja.models import TurnoCaja

@login_required
def caja(request, turno_id=None):
    fecha_str = request.GET.get("fecha")
    fecha = None

    if fecha_str:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        
    if turno_id:
        movimientos = movimientos_caja(request, turno_id=turno_id)
    else:
        movimientos = movimientos_caja(request, fecha=fecha)
        
    ventas = [m.venta for m in movimientos if m.venta]
    context = {
        "movimientos": movimientos,
        "ventas": ventas,
    }
    return render(request, 'caja/caja_diaria.html', context)

@login_required
def abrir_caja(request):
    try:
        abrir(usuario=request.user)
        messages.success(request, "Caja abierta correctamente")
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect("inicio")

@login_required
def cerrar_caja(request):
    if request.method == "POST":
        monto_raw = request.POST.get("monto_cierre")

        try:
            monto_cierre = Decimal(monto_raw)
        except (InvalidOperation, TypeError):
            messages.error(request, "Monto inválido.")
            return redirect("inicio")

        turno = obtener_turno_abierto(request.user)

        if not turno:
            messages.warning(request, "No hay una caja abierta.")
            return redirect("inicio")

        try:
            turno, _, _ = cerrar(turno, monto_cierre)

            messages.success(
                request,
                f"Caja cerrada."
            )

        except ValidationError as e:
            messages.error(request, str(e))

    return redirect("inicio")

@login_required
def ver_turnos(request):
    fecha = request.GET.get("fecha")
    
    context = {
        "turnos": arqueos_caja(fecha=fecha)
    }
    return render(request, 'turnos/turnos.html', context)

def crear_egreso(request):
    if request.method == "POST":
        try:
            turno_id = request.POST.get("turno_id")
            monto = request.POST.get("monto")
            concepto = request.POST.get("concepto")

            # Validaciones básicas
            if not turno_id:
                raise ValidationError("Debe seleccionar un turno.")

            if not monto or float(monto) <= 0:
                raise ValidationError("El monto debe ser mayor a 0.")

            # Obtener turno
            turno = TurnoCaja.objects.get(id=turno_id)

            # Validar que esté abierto (extra seguridad)
            if turno.fecha_cierre:
                raise ValidationError("El turno está cerrado.")

            # Registrar egreso (service)
            registrar_egreso(
                turno=turno,
                monto=monto,
                concepto=concepto,
                usuario=request.user
            )

            messages.success(request, "Egreso registrado correctamente.")
            return redirect("page_gastos")

        except TurnoCaja.DoesNotExist:
            messages.error(request, "El turno no existe.")

        except ValidationError as e:
            messages.error(request, str(e))

        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

    return redirect("page_gastos")