"""Urls de API Rest."""
from django.conf.urls import url, include
from rest_framework import routers
from api.views import actors, query, category, email, authorization, plan, chat

# registro de url para consultar usuarios
# servicio requerido por la web para la autenticacion
router = routers.DefaultRouter()
router.register(r'users', actors.UserViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    # Clientes
    url(r'^clients/$', actors.ClientListView.as_view(), name='clients'),
    # Servicio para logueo de clientes
    url(r'^clients-users/(?P<username>[^@]+@[^@]+\.[^@]+)/$', actors.ClientDetailByUsername.as_view(),
        name='client-detail-username'),
    #todos los planes activos de un cliente
    url(r'^clients/plans/$', plan.ClientPlansView.as_view(), name='client-plans'),

    url(r'^specialists-users/(?P<username>[^@]+@[^@]+\.[^@]+)/$', actors.SpecialistDetailByUsername.as_view(),
        name='specialist-detail-username'),

    url(r'^sellers-users/(?P<username>[^@]+@[^@]+\.[^@]+)/$', actors.SellerDetailByUsername.as_view(),
        name='seller-detail-username'),
    # detalle de cliente
    url(r'^clients/(?P<pk>[0-9]+)/$', actors.ClientDetailView.as_view(), name='client-detail'),
    # Especialidades
    url(r'^categories/$', category.CategoryListView.as_view(), name='categories'),
    url(r'^categories/(?P<pk>[0-9]+)/$', category.CategoryDetailView.as_view(), name='category-detail'),
    # Especialistas
    url(r'^specialists/$', actors.SpecialistListView.as_view(), name='specialists'),
    # Especialistas mensajes
    url(r'^specialists/list-messages/$', actors.SpecialistMessagesListView.as_view(), name='specialists-list-messages'),

    url(r'^specialists/(?P<pk>[0-9]+)/$', actors.SpecialistDetailView.as_view(), name='specialist-detail'),
    #numero de consultas mensual y anual de un especialista
    url(r'^specialists/query-count/$', actors.SpecialistQueryCountView.as_view(), name='specialist-query-count'),

    url(r'^account_status/specialists/(?P<pk>[0-9]+)/$',
        actors.SpecialistAccountView.as_view(), name='specialist-account-status'),
    # Consultas
    # Listado de Consultas por especialista
    # url(r'^specialist-queries/$', query.QueryListSpecialistView.as_view(), name='queries-specialist'),

    # Listado de Consulta y Creación de consultas por cliente
    url(r'^client/queries/$', query.QueryListClientView.as_view(), name='queries-client'),
    # Queries de cliente por categoria
    url(r'^queries/categories/(?P<pk>[0-9]+)/$', query.QueryChatClientView.as_view(), name='query-chat-client'),
    # Consultas de especialista por cliente
    url(r'^queries/clients/(?P<pk>[0-9]+)/$', query.QueryChatSpecialistView.as_view(), name='query-chat-specialist'),

    url(r'^queries/(?P<pk>[0-9]+)/$', query.QueryDetailView.as_view(), name='query-detail'),
    url(r'^query-last/(?P<category>[0-9]+)/$', query.QueryLastView.as_view(), name='last-query-bycategory'),
    # Vendedores
    url(r'^sellers/$', actors.SellerListView.as_view(), name='sellers'),
    url(r'^sellers/(?P<pk>[0-9]+)/$', actors.SellerDetailView.as_view(), name='seller-detail'),
    url(r'^account_status/sellers/(?P<pk>[0-9]+)/$', actors.SellerAccountView.as_view(), name='seller-account-status'),

    # Actualizar Consulta por detalle (Responder)
    url(r'^specialist/queries/(?P<pk>[0-9]+)/$', query.QueryDetailSpecialistView.as_view(), name='query-specialist'),
    # Contacto no efectivo
    url(r'^contacts/$', actors.ContactListView.as_view(), name='contacts'),
    # url para subir imagen
    url(r'^upload_photo/(?P<pk>[0-9]+)/$', actors.PhotoUploadView.as_view(), name='upload-photo'),
    url(r'^upload/$', actors.FileUploadView.as_view(), name='upload'),
    url(r'^upload_document/(?P<pk>[0-9]+)/$', actors.DocumentUploadView.as_view(), name='upload-document'),

    # url(r'^upload_archivo/(?P<filename>[^/]+)$', actors.AllFileUploadView.as_view())

    # chat (prueba con channels)
    url(r'^chat/$', chat.chat, name='chat'),
    # email
    url(r'^mail/$', email.mail, name='mails'),
    # servicio exclusivo para devolver key, solo para equipo de desarrollo
    url(r'^key/(?P<pk>[0-9]+)/$', actors.ViewKey.as_view(), name='get-key'),

    # servicio exclusivo para cambiar clave, solo para equipo de desarrollo
    url(r'^password/(?P<pk>[0-9]+)/$', actors.UpdatePasswordView.as_view(), name='update-pass'),

    # autorizacion para cliente
    url(r'^authorizations/clients/$', authorization.ClientListView.as_view(),
        name='auth-list-clients'),
    url(r'^authorizations/clients/(?P<pk>[0-9]+)/$', authorization.ChangeStatusClientView.as_view(),
        name='auth-clients'),

    # Activacion de planes
    url(r'^activations/plans/(?P<code>[0-9a-zA-Z]+)/$',
        plan.ActivationPlanView.as_view(), name='activation-plan'),

    # Plan Principal Elegido
    url(r'^chosens-plans/$', plan.ChosemPlanView.as_view(), name='chosen-plan'),

    #editar o detallar plan
    url(r'^chosens-plans/(?P<pk>[0-9]+)/$', plan.QueryPlansAcquiredDetailView.as_view(), name='chosen-plan-edit'),
]
