from django.db.models import Sum, Case, When, DecimalField, F, ExpressionWrapper, Value, Subquery, OuterRef, Max
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import datetime
from calendar import monthrange
from .models import Venta, DetalleVenta
from apps.caja.models import Caja
from apps.gasto.models import Gasto

def subquery_caja_egreso_dia(fecha):
    subquery = (
        Caja.objects
            .filter(tipo="EGRESO", fecha=OuterRef(fecha))
            .values("fecha")
            .annotate(total=Sum("monto"))
            .values("total")[:1]
    )
    return subquery

def subquery_caja_egreso_mes(fecha):
    return (
        Caja.objects
        .filter(tipo="EGRESO")
        .annotate(periodo=TruncMonth("fecha"))
        .filter(periodo=OuterRef(fecha))
        .values("periodo")
        .annotate(total=Sum("monto"))
        .values("total")[:1]
    )

def subquery_gastos(fecha):
    subquery = (
        Gasto.objects
            .annotate(periodo=TruncMonth("fecha"))
            .filter(periodo=OuterRef(fecha))
            .values("periodo")
            .annotate(total=Sum("monto"))
            .values("total")[:1]
    )   
    return subquery
    
def listar_ventas_dia(fecha=None, mes=None):
    ventas = Venta.objects.filter(estado=True)

    # Filtro por día
    if fecha:
        ventas = ventas.filter(fecha__date=fecha)

    # Filtro por mes
    elif mes:
        fecha_obj = datetime.strptime(mes, "%Y-%m")
        anio = fecha_obj.year
        mes_num = fecha_obj.month

        ventas = ventas.filter(
            fecha__year=anio,
            fecha__month=mes_num
        )
    gastos_subquery = subquery_caja_egreso_dia(fecha="periodo")
    ventas = (
        ventas
        .annotate(periodo=TruncDate("fecha"))
        .annotate(
            gastos=Subquery(gastos_subquery, output_field=DecimalField()),
        )
        .values("periodo")
        .annotate(
            total_qr=Sum(
                Case(
                    When(
                        metodo_pago="QR",
                        then=F("detalles__precio_unitario") * F("detalles__cantidad")
                    ),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_efectivo=Sum(
                Case(
                    When(
                        metodo_pago="Efectivo",
                        then=F("detalles__precio_unitario") * F("detalles__cantidad")
                    ),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_dia=Sum(
                F("detalles__precio_unitario") * F("detalles__cantidad"),
                output_field=DecimalField()
            ),
            total_costo=Sum(
                F("detalles__costo_unitario") * F("detalles__cantidad"),
                output_field=DecimalField()
            ),
            gastos=Max("gastos")
        )
        .annotate(
            utilidad=ExpressionWrapper(
                F("total_dia") - F("total_costo") - F("gastos"),
                output_field=DecimalField()
            )
        )
        .order_by("-periodo")
    )

    return ventas

def listar_ventas_mes(mes=None):
    queryset = DetalleVenta.objects.all()

    if mes:
        fecha_obj = datetime.strptime(mes, "%Y-%m")
        anio = fecha_obj.year
        mes_num = fecha_obj.month

        queryset = queryset.filter(
            venta__fecha__year=anio,
            venta__fecha__month=mes_num
        )
    gasto_subquery = subquery_gastos(fecha="periodo")
    caja_subquery = subquery_caja_egreso_mes(fecha="periodo")
    ventas = (
        queryset
        .annotate(periodo=TruncMonth('venta__fecha'))
        .annotate(
            total_gasto_g=Subquery(gasto_subquery, output_field=DecimalField()),
            total_gasto_c=Subquery(caja_subquery, output_field=DecimalField()),
        )
        .values('periodo')
        .annotate(
            total_qr=Sum(
                Case(
                    When(
                        venta__metodo_pago='QR',
                        then=F('precio_unitario') * F('cantidad')
                    ),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ),
            total_efectivo=Sum(
                Case(
                    When(
                        venta__metodo_pago='Efectivo',
                        then=F('precio_unitario') * F('cantidad')
                    ),
                    default=Value(0),
                    output_field=DecimalField()
                )
            ),
            total_dia=Sum(F('precio_unitario') * F('cantidad')),
            total_costo=Sum(F('costo_unitario') * F('cantidad')),
            gastos=Max(
                F("total_gasto_g") + F("total_gasto_c"),
                output_field=DecimalField()
            ),
        )
        .annotate(
            utilidad=F('total_dia') - F('total_costo') - F('gastos'),
        )
        .order_by('-periodo')
    )
    return ventas

def productos_vendidos(fecha=None, mes=None):
    
    filtros = {
        "venta__estado": True
    }

    # Filtro por día
    if fecha:
        filtros["venta__fecha__date"] = fecha

    # Filtro por mes (YYYY-MM)
    elif mes:
        fecha_obj = datetime.strptime(mes, "%Y-%m")
        anio = fecha_obj.year
        mes_num = fecha_obj.month

        ultimo_dia = monthrange(anio, mes_num)[1]

        fecha_inicio = datetime(anio, mes_num, 1)
        fecha_fin = datetime(anio, mes_num, ultimo_dia, 23, 59, 59)

        filtros["venta__fecha__range"] = (fecha_inicio, fecha_fin)
        
    detalles = (
        DetalleVenta.objects
        .filter(**filtros)
        .values(
            "producto__categoria__id",
            "producto__categoria__nombre",
            "producto__id",
            "producto__nombre",
        )
        .values(
            "producto__categoria__id",
            "producto__categoria__nombre",
            "producto__id",
            "producto__nombre",
        )
        .annotate(
            precio_venta=F("producto__precio_venta"),
            cantidad_total=Sum("cantidad"),

            ingreso_total=Sum(
                F("precio_unitario") * F("cantidad"),
                output_field=DecimalField()
            ),

            costo_total=Sum(
                F("costo_unitario") * F("cantidad"),
                output_field=DecimalField()
            ),
        )
        .annotate(
            ganancia=ExpressionWrapper(
                F("ingreso_total") - F("costo_total"),
                output_field=DecimalField()
            )
        )
        .order_by("producto__categoria__nombre", "-cantidad_total")
    )

    return detalles