"""Urls de API Rest."""
from django.conf.urls import url, include
from rest_framework import routers
from api.views import actors, query, category, email, authorization, payment
from api.views import validations, plan, chat, oauth, static_data, purchase
from api.views import account
# registro de url para consultar usuarios
# servicio requerido por la web para la autenticacion
router = routers.DefaultRouter()
router.register(r'users', actors.UserViewSet)

# app_name = 'api'

urlpatterns = [
    url(r'^', include(router.urls)),
    # Clientes
    url(r'^clients/$', actors.ClientListView.as_view(), name='clients'),
    # Servicio para logueo de clientes
    url(r'^clients-users/(?P<username>[^@]+@[^@]+\.[^@]+)/$',
        actors.ClientDetailByUsername.as_view(),
        name='client-detail-username'),
    # todos los planes activos de un cliente
    url(r'^clients/plans/$', plan.ClientPlansView.as_view(),
        name='client-plans'),

    url(r'^clients/plans-all/$', plan.ClientAllPlansView.as_view(),
        name='client-plans-all'),

    url(r'^clients/plans/(?P<pk>[0-9]+)/$', plan.ClientPlansDetailView.as_view(),
        name='client-plans-detail'),

    # Transferir plan de consultas
    url(r'^clients/plans-transfer/$', plan.ClientTransferPlansView.as_view(),
        name='client-plans-transfer'),
    # Compartir plan de consultas
    url(r'^clients/plans-share/$', plan.ClientSharePlansView.as_view(),
        name='client-plans-share'),
    # Facultar plan de consultas
    url(r'^clients/plans-empower/$', plan.ClientEmpowerPlansView.as_view(),
        name='client-plans-empower'),

    # Facultar plan de consultas
    url(r'^clients/plans-delete-empower/$', plan.ClientDeleteEmpowerPlansView.as_view(),
        name='plans-delete-empower'),

    # Facultar plan de consultas
    url(r'^clients/plans-share-empower/(?P<pk>[0-9]+)$', plan.ClientShareEmpowerPlansView.as_view(),
        name='client-plans-share-empower'),

    # Facultar plan de consultas
    url(r'^clients/email-check-operation/$', plan.ClientCheckEmailOperationView.as_view(),
        name='client-email-check-operation'),

    url(r'^specialists-users/(?P<username>[^@]+@[^@]+\.[^@]+)/$',
        actors.SpecialistDetailByUsername.as_view(),
        name='specialist-detail-username'),

    url(r'^sellers-users/(?P<username>[^@]+@[^@]+\.[^@]+)/$',
        actors.SellerDetailByUsername.as_view(),
        name='seller-detail-username'),

    # listado de planes a la venta
    url(r'^plans/$', plan.PlansView.as_view(),
        name='plans'),

    url(r'^plans/check_status$', plan.PlansStatus.as_view(),
        name='plans-status'),

    # crear planes no facturables
    url(r'^plans/plans-nonbillable/$', plan.PlansNonBillableView.as_view(),
        name='plans-nonbillable'),
    # planes no facturables ver vendedor
    url(r'^seller/plans-nonbillable/$',
        plan.PlansNonBillableSellerView.as_view(),
        name='seller-plans-nonbillable'),

    # # Envio de codigo de verificar al correo
    url(r'^send-code-password/$', actors.SendCodePassword.as_view(),
        name='send-code-password'),
    # # Validacion de codigo para reseteo de contrasena
    url(r'^valid-code-password/$', actors.ValidCodePassword.as_view(),
        name='valid-code-password'),
    # # reseteo de contraseña
    url(r'^reset-password-recovery/(?P<pk>[0-9]+)/$',
        actors.UpdatePasswordRecoveryView.as_view(),
        name='reset-password-recovery'),
    # actualizar de email
    url(r'^update-email/(?P<pk>[0-9]+)/$',
        actors.UpdateEmailUserView.as_view(), name='update-email'),

    # chequear data de filtrado
    url(r'^check-data/$',
        validations.CheckData.as_view(), name='check-data'),

    # detalle de cliente
    url(r'^clients/(?P<pk>[0-9]+)/$', actors.ClientDetailView.as_view(),
        name='client-detail'),

    url(r'^objections/$', static_data.ObjectionsListView.as_view(),
        name='objections'),
    # Especialidades
    url(r'^categories/$', category.CategoryListView.as_view(),
        name='categories'),
    url(r'^categories/(?P<pk>[0-9]+)/$',
        category.CategoryDetailView.as_view(), name='category-detail'),
    # Especialistas
    url(r'^specialists/$', actors.SpecialistListView.as_view(),
        name='specialists'),
    # Especialistas mensajes
    url(r'^specialists/list-messages/$',
        actors.SpecialistMessagesListView.as_view(),
        name='specialists-list-messages'),

    url(r'^specialists/(?P<pk>[0-9]+)/$',
        actors.SpecialistDetailView.as_view(),
        name='specialist-detail'),
    # numero de consultas mensual y anual de un especialista
    url(r'^specialists/query-count/$',
        actors.SpecialistQueryCountView.as_view(),
        name='specialist-query-count'),

    url(r'^specialists/associate/$',
        actors.SpecialistAsociateListView.as_view(),
        name='specialists-associate-category'),

    # Especialistas Asociados
    url(r'^specialists-asociate/$', actors.SpecialistAsociateListByQueryView.as_view(),
        name='specialists-asociate'),

    # Estados de Cuenta

    url(r'^account_status/specialist/(?P<pk>[0-9]+)/$',
        account.SpecialistAccountView.as_view(),
        name='specialists-account'),
    # Consultas
    # Listado de Consultas por especialista
    # url(r'^specialist-queries/$', query.QueryListSpecialistView.as_view(),
    # name='queries-specialist'),

    # Listado de Consulta y Creación de consultas por cliente
    url(r'^client/queries/$',
        query.QueryListClientView.as_view(),
        name='queries-client'),
    # Queries de cliente por categoria
    url(r'^queries/categories/(?P<pk>[0-9]+)/$',
        query.QueryChatClientView.as_view(),
        name='query-chat-client'),
    # Consultas de especialista por cliente
    url(r'^queries/clients/(?P<pk>[0-9]+)/$',
        query.QueryChatSpecialistView.as_view(),
        name='query-chat-specialist'),
    # Reconsulta
    url(r'^client/queries/(?P<pk>[0-9]+)/$',
        query.QueryDetailClientView.as_view(), name='query-client'),
    # Negacion de reconsulta
    url(r'^client/deny_requery/$',
        query.DeclineRequeryView.as_view(), name='query-deny-requery'),
    # Calificar consulta
    url(r'^client/qualify/queries/(?P<pk>[0-9]+)/$',
        query.SetQualificationView.as_view(), name='query-qualify'),
    # leer mensajes pendientes
    url(r'^client/messages/read_pending/$',
        query.ReadPendingAnswerView.as_view(), name='read-pending-answer'),
    # Subida de archivos a la consulta (pk)
    url(r'^queries/upload_files/(?P<pk>[0-9]+)/$',
        query.QueryUploadFilesView.as_view(), name='query-upload-files'),

    url(r'^query-last/(?P<category>[0-9]+)/$', query.QueryLastView.as_view(), name='last-query-bycategory'),
    url(r'^queries-messages/(?P<pk>[0-9]+)/$', query.QueryMessageView.as_view(), name='query-messages'),

    # Specialist Accept Query
    url(r'^query-accept/(?P<pk>[0-9]+)/$', query.QueryAcceptView.as_view(),
        name='query-accept'),
    # Specialist Derive Query
    url(r'^query-derive/(?P<pk>[0-9]+)/$', query.QueryDeriveView.as_view(),
        name='query-derive'),
    # Specialist Decline Query
    url(r'^query-decline/(?P<pk>[0-9]+)/$', query.QueryDeclineView.as_view(),
        name='query-decline'),

    # Vendedores
    url(r'^sellers/$', actors.SellerListView.as_view(), name='sellers'),
    url(r'^sellers/(?P<pk>[0-9]+)/$', actors.SellerDetailView.as_view(),
        name='seller-detail'),
    url(r'^account_status/sellers/(?P<pk>[0-9]+)/$', actors.SellerAccountView.as_view(), name='seller-account-status'),

    # Actualizar Consulta por detalle (Responder)
    url(r'^specialist/queries/(?P<pk>[0-9]+)/$',
        query.QueryDetailSpecialistView.as_view(), name='query-specialist'),

    # Contacto no efectivo
    url(r'^contacts/$', actors.ContactListView.as_view(), name='contacts'),
    # url para subir imagen
    url(r'^upload_photo/(?P<pk>[0-9]+)/$', actors.PhotoUploadView.as_view(), name='upload-photo'),
    url(r'^upload/$', actors.FileUploadView.as_view(), name='upload'),
    url(r'^upload_document/(?P<pk>[0-9]+)/$', actors.DocumentUploadView.as_view(), name='upload-document'),
    # cambiar clave de usuario
    url(r'^change/password/(?P<pk>[0-9]+)/$',
        actors.UpdateUserPassword.as_view(),
        name='update-password'),
    # url(r'^upload_archivo/(?P<filename>[^/]+)$', actors.AllFileUploadView.as_view())

    # chat (prueba con channels)
    url(r'^chat/$', chat.chat, name='chat'),
    # email
    url(r'^mail/$', email.mail, name='mails'),


    # autorizacion para cliente
    url(r'^authorizations/clients/$', authorization.ClientListView.as_view(),
        name='auth-list-clients'),
    url(r'^authorizations/clients/(?P<pk>[0-9]+)/$', authorization.ChangeStatusClientView.as_view(),
        name='auth-clients'),

    # Test auth
    url(r'^oauth/$', oauth.TestOAuth.as_view(), name='oauth-test'),

    # Activacion de planes
    url(r'^activations/plans/(?P<code>[0-9a-zA-Z]+)/$',
        plan.ActivationPlanView.as_view(), name='activation-plan'),

    # Plan Principal Elegido
    url(r'^chosens-plans/$', plan.ChosenPlanView.as_view(), name='chosen-plan'),

    # Editar o Detallar plan adquirido
    url(r'^chosens-plans/(?P<pk>[0-9]+)/$',
        plan.QueryPlansAcquiredDetailView.as_view(), name='chosen-plan-edit'),

    # Api RUC Publico
    url(r'^ruc/(?P<pk>[0-9]+)/$', actors.RucDetailView.as_view(), name='ruc-detail'),

    # Only DEVs
    # servicio exclusivo para devolver key, solo para equipo de desarrollo
    url(r'^key/(?P<pk>[0-9]+)/$', actors.ViewKey.as_view(), name='get-key'),
    # servicio exclusivo para cambiar clave, solo para equipo de desarrollo
    url(r'^password/(?P<pk>[0-9]+)/$', actors.UpdatePasswordView.as_view(),
        name='update-pass'),

    # Compras
    url(r'^purchase/$',
        purchase.CreatePurchase.as_view(), name='purchase'),

    # Pagos
    url(r'^payment/$',
        payment.CreatePayment.as_view(), name='payment'),

    url(r'^payment-pending/$',
        payment.PaymentPendingView.as_view(), name='payment-pending'),

]
