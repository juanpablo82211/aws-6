from django.contrib import admin
from django.urls import path
from hello.views import user_dashboard, crear_usuario, editar_calorias

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_dashboard, name='dashboard'),
    path('crear/', crear_usuario, name='crear'),
    path('editar_calorias/<str:usuario_id>/', editar_calorias, name='editar_calorias'),  # Aquí faltaba la vista
]
