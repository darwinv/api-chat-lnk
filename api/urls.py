from django.conf.urls import url, include
from rest_framework import routers, viewsets
from api import views
from api.views import actors, querys, category

# registro de url para consultar usuarios
# servicio requerido por la web para la autenticacion
router = routers.DefaultRouter()
router.register(r'users', actors.UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),

    url(r'^clients/$', actors.ClientListView.as_view(), name='clients'),
    url(r'^clients/(?P<pk>[0-9]+)/$', actors.ClientDetailView.as_view(), name='client-detail'),
    url(r'^categories/$', category.CategoryListView.as_view(), name='categories'),
    url(r'^categories/(?P<pk>[0-9]+)/$', category.CategoryDetailView.as_view(), name='category-detail'),
    url(r'^specialists/$', actors.SpecialistListView.as_view(), name='specialists'),
    url(r'^specialists/(?P<pk>[0-9]+)/$', actors.SpecialistDetailView.as_view(), name='specialist-detail'),
    url(r'^account_status/specialists/(?P<pk>[0-9]+)/$', actors.SpecialistAccountView.as_view(), name='specialist-account-status'),
    url(r'^queries/$', querys.QueryListView.as_view(), name='queries'),
    url(r'^sellers/$', actors.SellerListView.as_view(), name='sellers'),

]
