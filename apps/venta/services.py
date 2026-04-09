from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from .models import Venta, DetalleVenta
from apps.caja.services import registrar_ingreso, obtener_turno_abierto

@transaction.atomic
def crear(usuario, metodo_pago, detalles):

    # 1️⃣ Crear venta con total inicial 0
    venta = Venta.objects.create(
        usuario=usuario,
        fecha=timezone.now(),
        metodo_pago=metodo_pago,
        total=Decimal("0.00")
    )

    # 2️⃣ Crear detalles
    for item in detalles:
        cantidad = item["cantidad"]
        precio = item["producto"].precio_venta
        subtotal = cantidad * precio
        detalle = DetalleVenta(
            venta=venta,
            producto=item["producto"],
            cantidad=item["cantidad"],
            precio_unitario=item["producto"].precio_venta, 
            costo_unitario=item["producto"].precio_costo,
            subtotal=subtotal
        )

        detalle.full_clean()
        detalle.save()
        
    venta.recalcular_total()
    
    if metodo_pago in ["Efectivo", "QR"]:
        turno = obtener_turno_abierto(usuario)

        registrar_ingreso(
            turno=turno,
            monto=venta.total,
            concepto=f"Venta #{venta.id}",
            usuario=usuario,
            venta=venta
        )
    return venta

def obtener_venta(venta_id):
    return Venta.objects.prefetch_related("detalles").get(id=venta_id)

def anular(venta_id):
    venta = Venta.objects.get(id=venta_id)
    venta.estado = False
    venta.save(update_fields=["estado"])
    return venta

def eliminar(venta_id):
    venta = Venta.objects.get(id=venta_id)
    venta.delete()
    

def detalle_ventas(usuario, fecha=None):
    fecha = fecha or timezone.localdate()
    ventas = Venta.objects.filter(fecha__date=fecha)
    roles_superiores = ["Administrador", "Supervisor"]

    if not usuario.is_superuser and not usuario.groups.filter(name__in=roles_superiores).exists():
        turno = obtener_turno_abierto(usuario)
        if turno:
            ventas = ventas.filter(caja__turno=turno)
        else:
            ventas = Venta.objects.none()

    ventas = ventas.prefetch_related("detalles__producto").order_by("usuario__username", "fecha")
    total_dia = ventas.aggregate(total=Sum("total"))["total"] or 0
    return ventas, total_dia, fecha

def calcular_totales(ventas):
    total_general = Decimal("0.00")
    total_costos = Decimal("0.00")
    total_gastos = Decimal("0.00")
    total_ganancia = Decimal("0.00")
    for v in ventas:
        print(v)
        
    for v in ventas:
        total_general += v.get("total_dia") or Decimal("0.00")
        total_costos += v.get("total_costo") or Decimal("0.00")
        total_gastos += v.get("gastos") or Decimal("0.00")
        total_ganancia += v.get("utilidad") or Decimal("0.00")

    return total_general, total_costos, total_gastos, total_ganancia
