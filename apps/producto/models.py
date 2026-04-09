from django.core.exceptions import ValidationError
from django.db import models
from apps.categoria.models import Categoria

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True, blank=False, null=False)
    precio_costo = models.DecimalField(max_digits=8, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = "producto"
        verbose_name = ("Producto")
        verbose_name_plural = ("Productos")

    def __str__(self):
        return self.nombre
    
    def clean(self):
        if self.precio_costo < 0 or self.precio_venta < 0:
            raise ValidationError("Los precios no pueden ser negativos")
        
        if self.precio_venta < self.precio_costo:
            raise ValidationError("El precio de venta no puede ser menor al precio de costo")

