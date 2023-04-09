from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
app_name = "store"

urlpatterns = [path('', views.index, name='index'),path('add_to_cart/<int:sneaker_id>/', views.add_to_cart, name='add_to_cart'),] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)