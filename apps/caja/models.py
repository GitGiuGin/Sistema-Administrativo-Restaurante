from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.safestring import mark_safe
from apps.venta.models import Venta

User = get_user_model()

class TurnoCaja(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    monto_apertura = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_cierre = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    abierta = models.BooleanField(default=True)
    
    class Meta:
        db_table = "turno_caja"
        verbose_name = "Turno de Caja"
        verbose_name_plural = "Turnos de Caja"
        ordering = ["-fecha_apertura"]

    def __str__(self):
        estado = "Abierta" if self.abierta else "Cerrada"
        return f"Turno {self.id} - {self.usuario} - {estado}"

    def clean(self):
        if self.abierta:
            turno_abierto = TurnoCaja.objects.filter(
                usuario=self.usuario,
                abierta=True
            ).exclude(pk=self.pk).exists()

            if turno_abierto:
                raise ValidationError("El usuario ya tiene un turno abierto.")
    
    @property
    def saldo(self):
        ingresos = self.caja_set.filter(tipo="INGRESO").aggregate(
            total=Sum("monto")
        )["total"] or 0

        egresos = self.caja_set.filter(tipo="EGRESO").aggregate(
            total=Sum("monto")
        )["total"] or 0

        return self.monto_apertura + ingresos - egresos
    
    @property
    def estado(self):
        if self.abierta:
            return mark_safe('<span class="badge bg-success">Abierta</span>')
        return mark_safe('<span class="badge bg-danger">Cerrada</span>')

class Caja(models.Model):
    TIPOS = (
        ("INGRESO", "Ingreso"),
        ("EGRESO", "Egreso"),
    )
    turno = models.ForeignKey(TurnoCaja, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=255)
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "caja"
        verbose_name = "Caja"
        verbose_name_plural = "Cajas"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} - {self.tipo} - {self.monto}"
    
    def clean(self):
        if not self.turno.abierta:
            raise ValidationError("No se pueden registrar movimientos en un turno cerrado.")
        
        if self.venta and self.tipo != "INGRESO":
            raise ValidationError("Una venta solo puede generar movimientos de ingreso.")
        
        if self.usuario:
            if not (
                self.usuario.is_superuser or
                self.usuario.groups.filter(name__in=["Administrador", "Supervisor"]).exists()
            ):
                if self.usuario != self.turno.usuario:
                    raise ValidationError("No puedes operar sobre este turno.")