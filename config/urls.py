from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de l'application blog
    path('', include('blog.urls')),
    
    # URLs d'authentification (fournies par Django)
    path('accounts/', include('django.contrib.auth.urls')),
]

# Servir les fichiers médias en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
