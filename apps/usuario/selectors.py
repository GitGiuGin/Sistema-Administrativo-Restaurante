from django.contrib.auth import get_user_model
from django.db.models import Case, When, Value, IntegerField, Min
from django.db.models.functions import Lower, Coalesce

def listar_usuarios(activos=None, search=None):
    User = get_user_model()

    usuarios = User.objects.prefetch_related('groups').all()

    # Filtro activo/inactivo
    if activos is True: 
        usuarios = usuarios.filter(is_active=True)
    elif activos is False:
        usuarios = usuarios.filter(is_active=False)

    # Filtro búsqueda
    if isinstance(search, str) and search.strip():
        usuarios = usuarios.filter(
            username__icontains=search.strip()
        )

    # Anotación para ordenar superusuario primero
    usuarios = usuarios.annotate(
    prioridad_super=Case(
            When(is_superuser=True, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by(
        'prioridad_super',
        'groups__id',
        Lower('last_name'),
        Lower('first_name')
    )

    return usuarios