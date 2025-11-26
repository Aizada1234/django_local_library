from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from catalog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),
    path('', RedirectView.as_view(url='catalog/', permanent=True)), 
    path('index/', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('logout/', views.logout_view, name='logout'),# ✅ логин/логаут
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
