from decimal import Decimal
from django.db import transaction
from django.forms import ValidationError
from django.utils import timezone
from apps.caja.models import Caja, TurnoCaja

def movimientos_caja(request, turno_id=None, fecha=None, tipo=None):
    user = request.user

    if user.is_superuser or user.groups.filter(name="Administrador").exists():
        movimientos = Caja.objects.all()

    elif user.groups.filter(name="Cajero").exists():
        turno = obtener_turno_abierto(user)
        movimientos = Caja.objects.filter(turno=turno)

    else:
        movimientos = Caja.objects.all()

    if turno_id:
        movimientos = movimientos.filter(turno_id=turno_id)

    if fecha:
        movimientos = movimientos.filter(fecha=fecha)
        
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)

    return movimientos.select_related("usuario", "venta").order_by("-fecha", "-id")

@transaction.atomic
def crear_movimiento_caja(data):
    turno = data.get("turno")

    if not turno or not turno.abierta:
        raise ValidationError("No hay un turno de caja abierto.")

    movimiento = Caja(**data)
    movimiento.full_clean()
    movimiento.save()
    return movimiento

def registrar_ingreso(turno, monto, concepto, usuario, venta=None):
    data = {
        "turno": turno,
        "tipo": "INGRESO",
        "monto": monto,
        "concepto": concepto,
        "usuario": usuario,
        "venta": venta
    }
    return crear_movimiento_caja(data)

def registrar_egreso(turno, monto, concepto, usuario):
    data = {
        "turno": turno,
        "tipo": "EGRESO",
        "monto": monto,
        "concepto": concepto,
        "usuario": usuario
    }
    return crear_movimiento_caja(data)

def obtener_turno_abierto(usuario):
    turno = TurnoCaja.objects.filter(usuario=usuario, abierta=True).first()
    # if not turno:
    #     raise ValidationError("No hay un turno de caja abierto para este usuario.")
    return turno

@transaction.atomic
def abrir(usuario, monto_apertura=None):
    if TurnoCaja.objects.filter(usuario=usuario, abierta=True).exists():
        raise ValidationError("El usuario ya tiene un turno de caja abierto.")
    
    if monto_apertura is None:
        monto_apertura = Decimal("50.00")
    turno = TurnoCaja(usuario=usuario, monto_apertura=monto_apertura)
    turno.full_clean()
    turno.save()
    return turno

@transaction.atomic
def cerrar(turno, monto_cierre):
    if not turno.abierta:
        raise ValidationError("El turno ya está cerrado.")

    saldo_esperado = turno.saldo
    diferencia = monto_cierre - saldo_esperado

    turno.fecha_cierre = timezone.now()
    turno.monto_cierre = monto_cierre
    turno.abierta = False

    turno.full_clean()
    turno.save()

    return turno, saldo_esperado, diferencia
