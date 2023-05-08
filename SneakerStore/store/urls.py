from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "store"

urlpatterns = [
                  path('', views.index, name='index'),
                  path('registar', views.registar, name='registar'),
                  path('login', views.login_view, name='login_view'),
                  path('perfil', views.perfil, name='perfil'),
                  path('logout', views.logout_view, name='logout'),
                  path('adicionar_carrinho/<int:sneaker_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
                  path('carrinho', views.carrinho, name='carrinho'),
                  path('login', auth_views.LoginView.as_view(), name='login'),
                  path('logout', auth_views.LogoutView.as_view(), name='logout'),
                  path('carrinho/remove/<int:sneaker_id>/', views.remove_from_cart, name='remove_from_cart'),
                  path('catalogo/', views.catalogo, name='catalogo'),
                  path('sobre_nos', views.sobre_nos, name='sobre_nos'),
                  path('detalhes/<int:sneaker_id>/', views.detalhes, name='detalhes'),
                  path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
                  path('finalizar/', views.editar_perfil, name='editar_perfil'),
                  path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
                  path('encomendas/', views.encomendas, name='encomendas'),
                  path('finalizar_compra/', views.finalizar_compra, name='finalizar_compra'),
                  path('editar_sneaker/<int:sneaker_id>/', views.editar_sneaker, name='editar_sneaker'),
                  path('remover_sneaker/<int:sneaker_id>/', views.remover_sneaker, name='remover_sneaker'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
