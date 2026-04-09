from re import search
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Producto

def crear_producto(data):
    producto = Producto(**data)
    producto.full_clean()
    producto.save()
    return producto

def listar_productos(activas=None, search=None):
    productos = Producto.objects.all()

    if activas is True:
        productos = productos.filter(estado=True)
    elif activas is False:
        productos = productos.filter(estado=False)
        
    if isinstance(search, str) and search.strip():
        productos = productos.filter(nombre__icontains=search.strip())

    return productos.order_by('categoria__nombre', 'nombre')

def actualizar_producto(producto_id, data):
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        raise ValidationError("El producto no existe")

    if "categoria_id" in data:
        producto.categoria_id = data["categoria_id"]

    for key, value in data.items():
        if key not in ["categoria_id"]:
            if key in ["precio_costo", "precio_venta"]:
                value = Decimal(value)
            setattr(producto, key, value)

    producto.full_clean()
    producto.save()
    return producto

def habilitar_producto(producto_id):
    producto = Producto.objects.get(id=producto_id)
    producto.estado = True
    producto.save()
    return producto

def inhabilitar_producto(producto_id):
    producto = Producto.objects.get(id=producto_id)
    producto.estado = False
    producto.save()
    return producto

def obtener_producto(producto_id):
    try:
        return Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        raise ValidationError("El producto no existe")

def listar_productos_ventas(activas=None, search=None):
    productos = Producto.objects.select_related("categoria")

    if activas is True:
        productos = productos.filter(
            estado=True,
            categoria__estado=True,
            categoria__ver_en_ventas=True
        )
    elif activas is False:
        productos = productos.filter(estado=False)

    if isinstance(search, str) and search.strip():
        productos = productos.filter(
            nombre__icontains=search.strip()
        )

    return productos.order_by('categoria__nombre', 'nombre')