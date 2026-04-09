from django.core.exceptions import ValidationError
from .models import Categoria

def crear_categoria(nombre, estado=True):
    categoria = Categoria(
        nombre=nombre.capitalize(),
        ver_en_ventas=True,
        estado=estado
    )
    categoria.full_clean() 
    categoria.save()
    return categoria

def listar_categorias(activas=None):
    categorias = Categoria.objects.all()

    if activas is True:
        categorias = categorias.filter(estado=True)
    elif activas is False:
        categorias = categorias.filter(estado=False)

    return categorias.order_by('nombre')

def obtener_categoria(categoria_id):
    try:
        return Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        return None
    
def toggle_ver_en_ventas(categoria_id):
    categoria = obtener_categoria(categoria_id)
    if not categoria:
        raise ValidationError("La categoría no existe")

    categoria.ver_en_ventas = not categoria.ver_en_ventas
    categoria.save(update_fields=["ver_en_ventas"])

    return categoria.ver_en_ventas

def habilitar_categoria(categoria_id):
    categoria = obtener_categoria(categoria_id)
    if not categoria:
        raise ValidationError("La categoría no existe")

    categoria.estado = True
    categoria.save(update_fields=["estado"])
    return True

def inhabilitar_categoria(categoria_id):
    categoria = obtener_categoria(categoria_id)
    if not categoria:
        raise ValidationError("La categoría no existe")

    categoria.estado = False
    categoria.ver_en_ventas = False
    categoria.save(update_fields=["estado", "ver_en_ventas"])
    return True

def categorias_ventas():
    categorias = Categoria.objects.filter(
        estado=True,
        ver_en_ventas=True
    ).order_by("nombre")

    return categorias