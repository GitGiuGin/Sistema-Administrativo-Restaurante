from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from apps.producto.services import listar_productos_ventas, obtener_producto
from apps.categoria.services import categorias_ventas
from .services import crear, detalle_ventas, calcular_totales
from .selectors import listar_ventas_dia, listar_ventas_mes, productos_vendidos
import json

@login_required
def page_ventas(request):
    carrito_temp = request.session.pop("carrito_temp", None)
    
    context = {
        "productos": listar_productos_ventas(activas=True),
        "categorias": categorias_ventas(),
        "carrito_temp": carrito_temp,
    }
    
    return render(request, "venta/registrar_pedido.html", context)

@login_required
def registrar_venta(request):
    if request.method == "POST":

        carrito_json = request.POST.get("carrito_data")
        metodo_pago = request.POST.get("metodo_pago")
        monto_recibido_raw = request.POST.get("monto_recibido")
        try:
            monto_recibido = Decimal(monto_recibido_raw)
        except InvalidOperation:
            messages.error(request, "Monto inválido")
            return redirect("ventas")
        
        if carrito_json:
            request.session["carrito_temp"] = json.loads(carrito_json)
            
        if not carrito_json:
            messages.warning(request, "El carrito está vacío 1")
            return redirect("ventas")
        
        if metodo_pago == "Efectivo":
            carrito = json.loads(carrito_json)
            total = Decimal("0.00")

            for item in carrito:
                producto = obtener_producto(item["id"])
                subtotal = producto.precio_venta * int(item["cantidad"])
                total += subtotal

            if monto_recibido < total:
                messages.warning(request, "El monto recibido es insuficiente")
                return redirect("ventas")
        
        if not metodo_pago:
            messages.warning(request, "Seleccione un método de pago")
            return redirect("ventas")

        carrito = json.loads(carrito_json)

        if len(carrito) == 0:
            messages.warning(request, "El carrito está vacío 2")
            return redirect("ventas")

        detalles = []

        for item in carrito:
            producto = obtener_producto(item["id"])

            detalles.append({
                "producto": producto,
                "cantidad": item["cantidad"],
            })

        try:
            venta = crear(
                usuario=request.user,
                metodo_pago=metodo_pago,
                detalles=detalles
            )
            
            # limpiar carrito
            if "carrito_temp" in request.session:
                del request.session["carrito_temp"]

            messages.success(
                request,
                f"Venta registrada correctamente. Total: Bs {venta.total}",
                extra_tags="redirect-ver_ventas"
            )

        except Exception as e:
            messages.error(request, str(e))

        return redirect("ventas")

@login_required    
def ver_ventas(request):
    fecha_str = request.GET.get("fecha")
    fecha = None
    if fecha_str:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    
    ventas, total, fecha = detalle_ventas(
        usuario=request.user,
        fecha=fecha)

    context = {
    "ventas": ventas,
    "total": total,
    "fecha": fecha,
}
    return render(request, "venta/detalle_ventas.html", context)

@login_required
def reporte_ventas_diaria(request):
    fecha = request.GET.get("fecha")
    mes = request.GET.get("mes")
    ventas = listar_ventas_dia(fecha=fecha, mes=mes)
    
    total_general, total_costos, total_ganancia = calcular_totales(ventas)
        
    context = {
        "ventas": ventas,
        "fecha": fecha,
        "total_general": total_general,
        "total_costos": total_costos,
        "total_ganancia": total_ganancia,
    }
    return render(request, "venta/reportes/ventas_diarias.html", context)

@login_required
def reporte_ventas_mensual(request):
    fecha = request.GET.get("mes")
    ventas = listar_ventas_mes(mes=fecha)
    
    total_general, total_costos, total_ganancia = calcular_totales(ventas)
        
    context = {
        "ventas": ventas,
        "fecha": fecha,
        "total_general": total_general,
        "total_costos": total_costos,
        "total_ganancia": total_ganancia,
        "tipo_reporte": "mensual",
    }
    return render(request, "venta/reportes/ventas_mensuales.html", context)

@login_required
def detalle_productos(request):
    fecha = request.GET.get("fecha")
    mes = request.GET.get("mes")

    fecha_obj = None
    fecha_mes = None

    if fecha:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")

    if mes:
        fecha_mes = datetime.strptime(mes, "%Y-%m")
    productos = productos_vendidos(fecha=fecha, mes=mes)

    categorias = defaultdict(lambda: {
        "productos": [],
        "total_cantidad": 0,
        "total_ingreso": 0,
        "total_costo": 0,
        "total_ganancia": 0,
    })

    for item in productos:
        cat = item["producto__categoria__nombre"]

        categorias[cat]["productos"].append(item)
        categorias[cat]["total_cantidad"] += item["cantidad_total"]
        categorias[cat]["total_ingreso"] += item["ingreso_total"]
        categorias[cat]["total_costo"] += item["costo_total"]
        categorias[cat]["total_ganancia"] += item["ganancia"]

    return render(request, "venta/reportes/_detalle_producto.html", {
        "categorias": dict(categorias),
        "fecha": fecha_obj,
        "fecha_mes": fecha_mes,
    })