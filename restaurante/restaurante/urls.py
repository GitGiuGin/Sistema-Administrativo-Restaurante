from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from .views import inicio
from apps.usuario.views import login, logout, recover

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/', inicio, name="inicio"),
    path('caja/', include("apps.caja.urls")),
    path('categorias/', include("apps.categoria.urls")),
    path('productos/', include("apps.producto.urls")),
    path('ventas/', include("apps.venta.urls")),
    path('user/', include("apps.usuario.urls")),
    path('gastos/', include("apps.gasto.urls")),
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('login/', login, name="login"),
    path("logout/", logout, name="logout"),
    path('recover/', recover, name="recover")
]