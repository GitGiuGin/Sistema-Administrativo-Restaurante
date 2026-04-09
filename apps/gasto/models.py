from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
User = get_user_model()

class Gasto(models.Model):
    CHOICES = [ 
            ("ALQUILER","Alquiler"),
            ("SERVICIOS","Servicios"),
            ("SUELDOS","Sueldos"),
            ("INSUMOS","Insumos"),
            ("OTROS","Otros"),
    ]
    
    concepto = models.CharField(max_length=200) 
    monto = models.DecimalField(max_digits=10, decimal_places=2) 
    categoria = models.CharField( max_length=50, choices=CHOICES) 
    descripcion = models.CharField(max_length=255, blank=True) 
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gasto"
        verbose_name = ("Gasto")
        verbose_name_plural = ("Gastos")

    def __str__(self):
        return self.concepto

    def clean(self):
        errores = {}

        # 1. Monto positivo
        if self.monto is not None and self.monto <= 0:
            errores['monto'] = "El monto debe ser mayor a 0"

        # 2. Concepto obligatorio con sentido
        if not self.concepto or len(self.concepto.strip()) < 3:
            errores['concepto'] = "El concepto debe tener al menos 3 caracteres"

        # 3. Descripción opcional pero útil si es OTROS
        if self.categoria == "OTROS" and not self.descripcion:
            errores['descripcion'] = "Debe ingresar una descripción cuando la categoría es OTROS"

        # 4. Fecha no puede ser futura (por seguridad)
        if self.fecha and self.fecha > timezone.now():
            errores['fecha'] = "La fecha no puede ser futura"

        if errores:
            raise ValidationError(errores)
