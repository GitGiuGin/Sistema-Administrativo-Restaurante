from urllib import request
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core import signing
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .services import User, crear_usuario, actualizar_usuario, habilitar_usuario, inhabilitar_usuario
from .selectors import listar_usuarios
from django.contrib.auth.models import Group
from .utils import get_user_role_level, get_available_groups_for_user, ROLE_HIERARCHY
User = get_user_model()

# Create your views here.
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect("inicio")
            else:
                messages.error(request, "Tu usuario está inactivo.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "usuario/auth/login.html")

@login_required
def logout(request):
    if request.method == "POST":
        auth_logout(request)
        return redirect("login")

    return redirect("login")

def recover(request):
    return render(request, "usuario/recover.html")

@login_required
def usuarios(request):
    tab = request.GET.get("tab", "habilitadas")

    if tab == "inhabilitadas":
        usuarios = listar_usuarios(activos=False)
    else:
        usuarios = listar_usuarios(activos=True)
        
    for u in usuarios:
        u.token = signing.dumps(u.id)
        
    for r in usuarios:
        r.role_level = get_user_role_level(r)


    context = {
        "usuarios": usuarios,
        "total": listar_usuarios().count(),
        "activos": listar_usuarios(activos=True).count(),
        "inactivos": listar_usuarios(activos=False).count(),
        "current_tab": tab,
        "user_level": get_user_role_level(request.user)
    }

    return render(request, 'usuario/page_usuarios.html', context)

@login_required
def form_usuario(request, token=None):
    user_level = get_user_role_level(request.user)

    # Determinar si es edición o creación
    if token:
        user_obj = get_object_or_404(User, token=token)
        modo = "editar"
    else:
        user_obj = None
        modo = "crear"

    if request.user.is_superuser:
        grupos = Group.objects.all()
    else:
        grupos = []
        for group in Group.objects.all():
            level = ROLE_HIERARCHY.get(group.name, 0)
            if level < user_level:
                grupos.append(group)

    context = {
        "modo": modo,
        "user_obj": user_obj,
        'grupos': grupos
    }
    return render(request, "usuario/form_usuario.html", context)

@login_required
def crear(request):
    grupos = get_available_groups_for_user(request.user)
    
    if request.method == "POST":
        selected_group_id = request.POST.get("group")
        
        context = {
            "grupos": grupos,
            "data": request.POST,
            "current_group_id": None
        }
        if not selected_group_id:
            messages.error(request, "Debe seleccionar un rol.")
            return render(request, "usuario/form_usuario.html", context)
        
        group = Group.objects.filter(id=selected_group_id).first()

        if not group:
            messages.error(request, "Rol inválido.")
            return render(request, "usuario/form_usuario.html", context)

        user_level = get_user_role_level(request.user)
        group_level = ROLE_HIERARCHY.get(group.name, 0)

        if not request.user.is_superuser and group_level >= user_level:
            messages.error(request, "No tienes permisos para asignar este rol.")
            return render(request, "usuario/form_usuario.html", context)

        data = {
            "first_name": request.POST.get("first_name").title(),
            "last_name": request.POST.get("last_name").title(),
            "telefono": request.POST.get("telefono"),
            "documento": request.POST.get("documento"),
            "zona": request.POST.get("zona").title(),
            "calle": request.POST.get("calle").title(),
            "numero_casa": request.POST.get("numero_casa"),
            "fecha_nacimiento": request.POST.get("fecha_nacimiento"),
            "group_id": selected_group_id
        }

        try:
            crear_usuario(data, created_by=request.user)
            messages.success(request, "Usuario creado correctamente.")
            return redirect('page_usuario')

        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)

            return render(request, "usuario/form_usuario.html", context)
            
@login_required
def editar(request, token):
    try:
        usuario_id = signing.loads(token)
    except signing.BadSignature:
        raise Http404("URL inválida")
    
    user_obj = get_object_or_404(User, id=usuario_id)
    signed_token = signing.dumps(user_obj.id)

    current_group_id = None
    grupo = user_obj.groups.first()
    current_group_id = grupo.id if grupo else None
    
    if request.method == "POST":  
        data = {
            "first_name": request.POST.get("first_name").title(),
            "last_name": request.POST.get("last_name").title(),
            "documento": request.POST.get("documento"),
            "telefono": request.POST.get("telefono"),
            "fecha_nacimiento": request.POST.get("fecha_nacimiento"),
            "zona": request.POST.get("zona").title(),
            "calle": request.POST.get("calle").title(),
            "numero_casa": request.POST.get("numero_casa"),
            "group_id": request.POST.get("group"),
        }

        try:
            actualizar_usuario(
                usuario_id=usuario_id,
                data=data,
                updated_by=request.user
            )

            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("page_usuario")

        except ValidationError as e:
            messages.error(request, e.message)
            
    grupos = get_available_groups_for_user(request.user)

    return render(request, "usuario/form_usuario.html", {
        "modo": "editar",
        "user_obj": user_obj,
        "grupos": grupos,
        "current_group_id": current_group_id,
        "token": signed_token
    })

@login_required
def detalle_usuario(request):
    from django.contrib.auth import get_user_model
    from django.shortcuts import get_object_or_404
    user_id = request.GET.get("id")

    User = get_user_model()
    user = get_object_or_404(User, id=user_id)

    return render(request, "usuario/_detalle_usuario.html", {
        "user": user
    })

@login_required
def habilitar(request, usuario_id):
    habilitar_usuario(usuario_id)
    messages.success(request, "Usuario habilitado correctamente.")
    return redirect(reverse('page_usuario') + '?tab=inhabilitadas')

@login_required
def inhabilitar(request, usuario_id):
    inhabilitar_usuario(usuario_id)
    messages.success(request, "Usuario inhabilitado correctamente.")
    return redirect(reverse('page_usuario') + '?tab=habilitadas')

@login_required
def page_perfil(request, user_id=None):
    if user_id:
        usuario = get_object_or_404(User, id=user_id)
    else:
        usuario = request.user

    contexto = {
        "usuario": usuario
    }
    return render(request, "usuario/perfil/page_perfil.html", contexto)

@login_required
def form_contraseña(request):
    from django.shortcuts import get_object_or_404

    user_id = request.GET.get("id")
    usuario = get_object_or_404(User, id=user_id)

    return render(request, "usuario/perfil/_form_contraseña.html", {
        "usuario": usuario
    })
    
@login_required
def cambiar_password(request):
    User = get_user_model()

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password_anterior = request.POST.get("password_anterior")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        usuario = get_object_or_404(User, id=user_id)

        if request.user != usuario and not request.user.is_superuser:
            messages.error(request, "No tienes permiso para cambiar esta contraseña")
        
        elif not usuario.check_password(password_anterior):
            messages.error(request, "La contraseña actual es incorrecta")
        
        elif password1 != password2:
            messages.error(request, "Las contraseñas nuevas no coinciden")
        
        elif len(password1) < 6:
            messages.warning(request, "La contraseña debe tener al menos 6 caracteres")
        
        else:
            usuario.set_password(password1)
            usuario.save()
            messages.success(request, "Contraseña actualizada correctamente")

        return render(request, "usuario/perfil/_form_contraseña.html", {
            "usuario": usuario
        })
        
@login_required
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user.set_password(settings.DEFAULT_PASSWORD)  # <- asegurarse de NO poner coma
    user.save()

    messages.success(request, f"Contraseña de {user.username} reiniciada correctamente")
    return redirect('page_usuario')