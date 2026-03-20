from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db import models
import re
from datetime import date

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True)
    documento = models.CharField(max_length=20, blank=True, unique=True)
    zona = models.CharField(max_length=100, blank=True)
    calle = models.CharField(max_length=150, blank=True)
    numero_casa = models.CharField(max_length=20, blank=True)   
    fecha_nacimiento = models.DateField(null=True, blank=True)

    def clean(self):
        errors = {}
        if self.telefono:
            if not re.fullmatch(r'^\+?\d{7,20}$', self.telefono):
                errors['telefono'] = "El número de teléfono debe tener entre 7 y 20 dígitos y puede empezar con +."
                
        if self.documento:
            if not re.fullmatch(r'^[A-Za-z0-9]{5,20}$', self.documento):
                errors['documento'] = "El documento debe tener entre 5 y 20 caracteres alfanuméricos."

        if self.fecha_nacimiento:
            if self.fecha_nacimiento > date.today():
                errors['fecha_nacimiento'] = "La fecha de nacimiento no puede ser futura."
            edad = (date.today() - self.fecha_nacimiento).days / 365.25
            if edad < 18:
                errors['fecha_nacimiento'] = "El usuario debe ser mayor de 18 años."

        if not self.zona or not self.calle or not self.numero_casa:
            errors['direccion'] = "La dirección no puede estar vacía."

        if self.documento and not self.telefono:
            errors['telefono'] = "Si se ingresa un documento, el teléfono también es obligatorio."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
    @property
    def puede_cerrar_caja(self):
        return self.is_superuser or self.groups.filter(name="Cajero").exists()
    
    @property
    def slug(self):
        if self.first_name and self.last_name:
            return slugify(f"{self.first_name}-{self.last_name}")
        return f"user-{self.id}"