from django.contrib import admin
from django.urls import path
from hello.views import user_dashboard, crear_usuario  # Asegúrate de importar las vistas correctamente

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_dashboard, name='dashboard'),
    path('crear/', crear_usuario, name='crear'),  # <--- Aquí está el nombre que se necesita
]
