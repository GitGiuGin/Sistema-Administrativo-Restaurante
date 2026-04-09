from django.contrib.auth.models import Group

ROLE_HIERARCHY = {
    "Administrador": 3,
    "Supervisor": 2,
    "Cajero": 1,
}

def get_user_role_level(user):
    if user.is_superuser:
        return 999  # Nivel máximo

    group = user.groups.first()
    if not group:
        return 0

    return ROLE_HIERARCHY.get(group.name, 0)

def get_available_groups_for_user(user):
    user_level = get_user_role_level(user)

    if user.is_superuser:
        return Group.objects.all()

    allowed_groups = []
    for group in Group.objects.all():
        level = ROLE_HIERARCHY.get(group.name, 0)
        if level < user_level:
            allowed_groups.append(group)

    return allowed_groups