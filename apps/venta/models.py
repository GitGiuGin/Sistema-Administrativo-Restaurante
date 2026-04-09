from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from apps.producto.models import Producto

User = get_user_model()

class Venta(models.Model):
    METODOS_PAGO = (
        ("EFECTIVO", "Efectivo"),
        ("QR", "QR"),
    )
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = "venta"
        verbose_name = ("Venta")
        verbose_name_plural = ("Ventas")

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha}"
    
    def recalcular_total(self):
        total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=["total"])
    
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        db_table = "detalle_venta"
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
    
    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")

        if self.precio_unitario <= 0:
            raise ValidationError("El precio unitario debe ser mayor a 0")

