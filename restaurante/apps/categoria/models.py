from django.core.exceptions import ValidationError
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, blank=False, null=False)
    estado = models.BooleanField(default=True)
    ver_en_ventas = models.BooleanField(default=False)

    class Meta:
        db_table = "categoria"
        verbose_name = ("Categoria")
        verbose_name_plural = ("Categorias")

    def __str__(self):
        return self.nombre
    
    @property
    def estado_texto(self):
        return "Activo" if self.estado else "Inactivo"
    
    @property
    def abreviatura(self):
        palabras = self.nombre.split()
        if len(palabras) > 1:
            return ''.join(p[0].upper() for p in palabras[:3])
        return self.nombre[:3].upper()
    
    def clean(self):
        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise ValidationError("El nombre no puede estar vacío.")
    
    