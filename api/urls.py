from django.conf.urls import url, include
from rest_framework import routers, viewsets
from api import views
from api.views import UserViewSet

# registro de url para consultar usuarios
# servicio requerido por la web para la autenticacion
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^clients/$', views.ClientListView.as_view(), name='clients'),
    url(r'^clients/(?P<pk>[0-9]+)/$', views.ClientDetailView.as_view(), name='client-detail'),
    url(r'^categories/$', views.CategoryListView.as_view(), name='categorys'),
    url(r'^categories/(?P<pk>[0-9]+)/$', views.CategoryDetailView.as_view(), name='category-detail'),
    url(r'^specialists/$', views.SpecialistListView.as_view(), name='specialists'),
    url(r'^specialists/(?P<pk>[0-9]+)/$', views.SpecialistDetailView.as_view(), name='specialist-detail'),
    url(r'^account_status/specialists/(?P<pk>[0-9]+)/$', views.SpecialistAccountView.as_view(), name='specialist-account-status'),
]
