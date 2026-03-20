from apps.gasto.models import Gasto

def crear(data):
    gasto = Gasto(**data)
    gasto.full_clean()
    gasto.save()
    return gasto

def listar(fecha=None):
    gastos = Gasto.objects.all()
    
    if fecha:
        gastos = gastos.filter(fecha__date=fecha)
        
    return gastos.order_by('-fecha')

def listar_categorias():
    return Gasto.CHOICES