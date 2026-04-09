from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from .utils import get_user_role_level, ROLE_HIERARCHY

User = get_user_model()
from .models import Usuario

def generar_username(first_name, last_name):
    particulas = ["de", "del", "la", "las", "los", "y"]

    nombres = first_name.strip().lower().split()
    apellidos_raw = last_name.strip().lower().split()
    apellidos = [a for a in apellidos_raw if a not in particulas]

    if not nombres or not apellidos:
        raise ValueError("Nombre o apellido inválido")

    primer_nombre = nombres[0]
    segundo_nombre = nombres[1] if len(nombres) > 1 else ""
    primer_apellido = apellidos[0]
    segundo_apellido = apellidos[1] if len(apellidos) > 1 else ""

    opciones = []

    opciones.append(f"{primer_nombre[0]}{primer_apellido}")

    if segundo_apellido:
        opciones.append(f"{primer_nombre[0]}{primer_apellido}{segundo_apellido[0]}")

    if segundo_nombre and segundo_apellido:
        opciones.append(f"{primer_nombre[0]}{segundo_nombre[0]}{primer_apellido}{segundo_apellido[0]}")

    for i in range(2, len(primer_nombre) + 1):
        opciones.append(f"{primer_nombre[:i]}{primer_apellido}")

    for username in opciones:
        if not Usuario.objects.filter(username=username).exists():
            return username

    # fallback con número
    base = f"{primer_nombre}{primer_apellido}"
    contador = 1
    while contador < 1000:
        username = f"{base}{contador}"
        if not Usuario.objects.filter(username=username).exists():
            return username
        contador += 1
        
def capitalizar_nombre(texto):
    palabras = texto.lower().split()
    return " ".join(p.capitalize() for p in palabras)

def capitalizar_apellido(texto):
    particulas = ["de", "del", "la", "las", "los", "y"]

    palabras = texto.lower().split()
    resultado = []

    for palabra in palabras:
        if palabra in particulas:
            resultado.append(palabra)
        else:
            resultado.append(palabra.capitalize())

    return " ".join(resultado)

@transaction.atomic
def crear_usuario(data, created_by=None):
    group_id = data.pop("group_id", None)

    first_name = capitalizar_nombre(data.get("first_name", "").strip())
    last_name = capitalizar_apellido(data.get("last_name", "").strip())
    data["first_name"] = first_name
    data["last_name"] = last_name
    
    username = generar_username(first_name, last_name)
    data["username"] = username

    user = User(**data)

    user.set_password(data.get("password", settings.DEFAULT_PASSWORD))
    user.is_staff = False
    user.full_clean()
    user.save()

    if group_id:
        group = Group.objects.get(id=group_id)

        if created_by and not created_by.is_superuser:
            creator_level = get_user_role_level(created_by)
            target_level = ROLE_HIERARCHY.get(group.name, 0)

            if target_level > creator_level:
                raise ValidationError("No puedes asignar un rol superior al tuyo.")

        user.groups.set([group])

    return user

@transaction.atomic
def actualizar_usuario(usuario_id, data, updated_by=None):
    try:
        user = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        raise ValidationError("El usuario no existe")
    
    if updated_by and not updated_by.is_superuser:

        updater_level = get_user_role_level(updated_by)
        target_user_level = get_user_role_level(user)

        # No puede editar usuarios de mismo o mayor nivel
        if target_user_level >= updater_level:
            raise ValidationError(
                "No puedes editar un usuario con el mismo o mayor nivel que tú."
            )

    group_id = data.pop("group_id", None)

    for key, value in data.items():
        setattr(user, key, value)

    user.full_clean()
    user.save()

    if group_id:
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise ValidationError("El rol seleccionado no existe.")

        if updated_by and not updated_by.is_superuser:
            updater_level = get_user_role_level(updated_by)
            new_role_level = ROLE_HIERARCHY.get(group.name, 0)

            # No puede asignar rol superior al suyo
            if new_role_level > updater_level:
                raise ValidationError(
                    "No puedes asignar un rol superior al tuyo."
                )

        user.groups.set([group])

    return user

def habilitar_usuario(usuario_id):
    user = User.objects.get(id=usuario_id)
    user.is_active = True
    user.save()
    return user

def inhabilitar_usuario(usuario_id):
    user = User.objects.get(id=usuario_id)
    user.is_active = False
    user.save()
    return user