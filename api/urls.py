"""Urls de API Rest."""
from django.conf.urls import url, include
from rest_framework import routers
from api.views import actors, query, category, email, authorization

# registro de url para consultar usuarios
# servicio requerido por la web para la autenticacion
router = routers.DefaultRouter()
router.register(r'users', actors.UserViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^clients/$', actors.ClientListView.as_view(), name='clients'),
    url(r'^clients-users/(?P<username>\w+)/$', actors.ClientDetailByUsername.as_view(), name='client-detail-username'),
    url(r'^clients/(?P<pk>[0-9]+)/$', actors.ClientDetailView.as_view(), name='client-detail'),
    url(r'^categories/$', category.CategoryListView.as_view(), name='categories'),
    url(r'^categories/(?P<pk>[0-9]+)/$', category.CategoryDetailView.as_view(), name='category-detail'),
    url(r'^specialists/$', actors.SpecialistListView.as_view(), name='specialists'),
    url(r'^specialists/(?P<pk>[0-9]+)/$', actors.SpecialistDetailView.as_view(), name='specialist-detail'),
    url(r'^account_status/specialists/(?P<pk>[0-9]+)/$',
        actors.SpecialistAccountView.as_view(), name='specialist-account-status'),
    url(r'^queries/$', query.QueryListView.as_view(), name='queries'),
    url(r'^queries/(?P<pk>[0-9]+)/$', query.QueryDetailView.as_view(), name='query-detail'),
    url(r'^query-last/(?P<category>[0-9]+)/$', query.QueryLastView.as_view(), name='last-query-bycategory'),
    url(r'^sellers/$', actors.SellerListView.as_view(), name='sellers'),
    url(r'^sellers/(?P<pk>[0-9]+)/$', actors.SellerDetailView.as_view(), name='seller-detail'),

    url(r'^account_status/sellers/(?P<pk>[0-9]+)/$', actors.SellerAccountView.as_view(), name='seller-account-status'),

    # url para subir imagen
    url(r'^upload_photo/(?P<pk>[0-9]+)/$', actors.PhotoUploadView.as_view(), name='upload-photo'),
    url(r'^upload/$', actors.FileUploadView.as_view(), name='upload'),
    url(r'^upload_document/(?P<pk>[0-9]+)/$', actors.DocumentUploadView.as_view(), name='upload-document'),

    # url(r'^upload_archivo/(?P<filename>[^/]+)$', actors.AllFileUploadView.as_view())

    # email
    url(r'^mail/$', email.mail, name='mails'),

    # Autorizaciones
    url(r'^authorizations-clients/$', authorization.ClientListView.as_view(), name='authorizations-clients'),

]
