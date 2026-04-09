from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from apps.categoria.models import Categoria
from .services import crear_categoria, listar_categorias, habilitar_categoria, inhabilitar_categoria, toggle_ver_en_ventas

@login_required
def page_categoria(request):
    categorias_habilitadas = listar_categorias(True)
    categorias_inhabilitadas = listar_categorias(False)

    context = {
        "categorias_habilitadas": categorias_habilitadas,
        "categorias_inhabilitadas": categorias_inhabilitadas,
    }
    
    return render(request, "categoria/page_categoria.html", context)

@login_required
def crear(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre', '').strip()

        if not nombre:
            messages.error(request, "El nombre es obligatorio.")
            return redirect('categorias')

        if len(nombre) < 3:
            messages.warning(request, "El nombre debe tener al menos 3 caracteres.")
            return redirect('categorias')

        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, "La categoría ya existe.")
            return redirect('categorias')

        crear_categoria(nombre, True)
        messages.success(request, "Categoría creada correctamente.")
        return redirect('categorias')

@login_required
def habilitar(request, categoria_id):
    habilitar_categoria(categoria_id)
    messages.success(request, "Categoría habilitada correctamente.")
    return redirect('categorias')

@login_required
def inhabilitar(request, categoria_id):
    inhabilitar_categoria(categoria_id)
    messages.success(request, "Categoría inhabilitada correctamente.")
    return redirect('categorias')

@require_POST
@login_required
def toggle_ver_en_ventas_view(request):
    categoria_id = request.POST.get("categoria_id")

    try:
        nuevo_valor = toggle_ver_en_ventas(categoria_id)
    except ValidationError as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

    return JsonResponse({
        "ok": True,
        "ver_en_ventas": nuevo_valor
    })