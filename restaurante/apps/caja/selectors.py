from apps.caja.models import TurnoCaja
from django.db.models import Sum, Case, When, F, DecimalField

def obtener_turno_abierto(usuario):
    return TurnoCaja.objects.filter(usuario=usuario, abierta=True).first()

def consultar_movimientos_caja(usuario):
    turno = obtener_turno_abierto(usuario)
    if turno:
        return turno.caja_set.all()
    return []

def arqueos_caja(fecha=None):
    arqueo = (
        TurnoCaja.objects
        .select_related("usuario")
    )

    if fecha:
        arqueo = arqueo.filter(fecha_apertura__date=fecha)

    arqueo = arqueo.annotate(
        total_qr=Sum(
            Case(
                When(caja__venta__metodo_pago="QR", then=F("caja__venta__total")),
                default=0,
                output_field=DecimalField()
            )
        ),
        total_efectivo=Sum(
            Case(
                When(caja__venta__metodo_pago="Efectivo", then=F("caja__venta__total")),
                default=0,
                output_field=DecimalField()
            )
        ),
        total_egreso=Sum(
            Case(
                When(caja__tipo="EGRESO", then=F("caja__monto")),
                default=0,
                output_field=DecimalField()
            )
        ),
    ).annotate(
        efectivo_neto=F("total_efectivo") - F("total_egreso"),
        diferencia=F("monto_cierre") - F("efectivo_neto")
    ).order_by("-fecha_apertura")

    return arqueo
    
def turnos_abiertos_operativo():
    return TurnoCaja.objects.filter(
                fecha_cierre__isnull=True
            ).select_related('usuario')