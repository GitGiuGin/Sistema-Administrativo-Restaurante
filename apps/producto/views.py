from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from .services import crear_producto, listar_productos, actualizar_producto, habilitar_producto, inhabilitar_producto
from apps.categoria.services import listar_categorias, obtener_categoria

@login_required
def page_productos(request):
    productos = listar_productos()
    productos_habilitados = listar_productos(True)
    productos_inhabilitados = listar_productos(False)
    categorias = listar_categorias(True)
    
    context = {
        "productos": productos,
        "productos_habilitados": productos_habilitados,
        "productos_inhabilitados": productos_inhabilitados,
        "categorias": categorias
    }
    return render(request, "producto/page_productos.html", context)

@login_required
def crear(request):
    if request.method == "POST":
        try:
            categoria_id = obtener_categoria(request.POST.get("categoria"))

            data = {
                "nombre": request.POST.get("nombre").capitalize(),
                "categoria": categoria_id,
                "precio_costo": request.POST.get("precio_costo"),
                "precio_venta": request.POST.get("precio_venta"),
                "estado": True
            }

            crear_producto(data)

            messages.success(
                request,
                f"Producto «{data['nombre']}» creado correctamente."
            )

        except ValidationError as e:
            if hasattr(e, "message_dict"):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        if field == "__all__":
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{field}: {error}")
            else:
                for error in e.messages:
                    messages.error(request, error)

        except Exception as e:
            # errores inesperados
            messages.error(
                request,
                "Ocurrió un error al crear el producto."
            )

    return redirect("productos")

@login_required
def editar(request, producto_id):
    if request.method == "POST":
        data = {
            "nombre": request.POST.get("nombre"),
            "precio_costo": request.POST.get("precio_costo"),
            "precio_venta": request.POST.get("precio_venta"),
            "categoria_id": request.POST.get("categoria_id"),
        }

        try:
            actualizar_producto(producto_id, data)
            messages.success(request, "Producto actualizado correctamente.")

        except ValidationError as e:
            if hasattr(e, "message_dict"):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        if field == "__all__":
                            messages.error(request, error)
                        else:
                            messages.error(request, f"{field}: {error}")
            else:
                for error in e.messages:
                    messages.error(request, error)

        except Exception:
            messages.error(request, "Ocurrió un error inesperado")

    return redirect("productos")

@login_required
def habilitar(request, producto_id):
    habilitar_producto(producto_id)
    messages.success(request, "Producto habilitado correctamente.")
    return redirect(reverse('productos') + '?tab=inhabilitadas')

@login_required
def inhabilitar(request, producto_id):
    inhabilitar_producto(producto_id)
    messages.success(request, "Producto inhabilitado correctamente.")
    return redirect('productos')

@login_required
def buscar(request):
    search = request.GET.get("q", "").strip()
    estado = request.GET.get("estado")

    if estado == "habilitado":
        productos = listar_productos(True, search)
        tipo = "habilitado"
    else:
        productos = listar_productos(False, search)
        tipo = "inhabilitado"

    html = render_to_string(
        "producto/_tabla_filas.html",
        {"productos": productos, "tipo": tipo},
        request=request
    )

    return JsonResponse({"html": html})


