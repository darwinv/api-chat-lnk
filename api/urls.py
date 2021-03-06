"""Urls de API Rest."""
from django.conf.urls import url, include
from rest_framework import routers
from api.views import actors, query, category, email, authorization, payment
from api.views import validations, plan, chat, oauth, static_data, purchase
from api.views import account, match, notification
# registro de url para consultar usuarios
# servicio requerido por la web para la autenticacion
router = routers.DefaultRouter()
router.register(r'users', actors.UserViewSet)

# app_name = 'api'

urlpatterns = [
    url(r'^', include(router.urls)),
    # Clientes
    url(r'^clients/$', actors.ClientListView.as_view(), name='clients'),
    # detalle de cliente
    url(r'^clients/(?P<pk>[0-9]+)/$', actors.ClientDetailView.as_view(),
        name='client-detail'),
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
    url(r'^clients/plans-share-empower/(?P<pk>[0-9]+)/$', plan.ClientShareEmpowerPlansView.as_view(),
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

    url(r'^sellers-users-id/(?P<pk>[0-9]+)/$',
        actors.SellerDetailByID.as_view(),
        name='seller-detail-id'),

    # listado de planes a la venta
    url(r'^plans/$', plan.PlansView.as_view(),
        name='plans'),

    url(r'^plans/check_status/$', plan.PlansStatus.as_view(),
        name='plans-status'),

    # crear planes no facturables
    url(r'^plans/plans-nonbillable/$', plan.PlansNonBillableView.as_view(),
        name='plans-nonbillable'),
    # planes no facturables ver vendedor
    url(r'^seller/plans-nonbillable/$',
        plan.PlansNonBillableSellerView.as_view(),
        name='seller-plans-nonbillable'),

    url(r'^seller/plans-nonbillable/contact/(?P<pk>[0-9]+)/$',
        plan.PlansNonBillableSellerByContactView.as_view(),
        name='seller-plans-nonbillable-by-contact'),

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
    url(r'^specialists-asociate/$',
        actors.SpecialistAsociateListByQueryView.as_view(),
        name='specialists-asociate'),


    # Estados de Cuenta cliente
    url(r'^account_status/client/(?P<pk>[0-9]+)/$',
        account.ClientAccountView.as_view(),
        name='clients-account'),

    # Estados de Cuenta especialista
    url(r'^account_status/specialist/(?P<pk>[0-9]+)/$',
        account.SpecialistAccountView.as_view(),
        name='specialists-account'),

    # footer especialista
    url(r'^footer/specialist/$',
        account.SpecialistFooterView.as_view(),
        name='footer-specialist'),

    # Estado de cuenta perfil vendedor
    url(r'^account_status/seller/(?P<pk>[0-9]+)/$',
        account.SellerAccountView.as_view(),
        name='sellers-account'),

    # url(r'^account_status/sellers/(?P<pk>[0-9]+)/$', actors.SellerAccountView.as_view(), name='seller-account-status'),

    # Estado de cuenta del vendedor
    url(r'^account_status/backend/seller/(?P<pk>[0-9]+)/$',
        account.SellerAccountBackendView.as_view(),
        name='sellers-account-back'),

    # footer seller
    url(r'^footer/seller/$',
        account.SellerFooterView.as_view(),
        name='footer-seller'),
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

    # Match
    url(r'^client/matchs/$',
        match.MatchListClientView.as_view(),
        name='match-client'),

    url(r'^match/(?P<pk>[0-9]+)/$',
        match.MatchDetail.as_view(), name='match-detail'),

    url(r'^match/upload_files/(?P<pk>[0-9]+)/$',
        match.MatchUploadFilesView.as_view(), name='match-upload-files'),

    url(r'^specialists/matchs/upload_files/(?P<pk>[0-9]+)/$',
        match.SpecialistMatchUploadFilesView.as_view(), name='specialists-match-files'),

    url(r'^clients/sales/upload_files/(?P<pk>[0-9]+)/$',
        match.SaleClientUploadFilesView.as_view(), name='client-sale-files'),

    # url(r'^clients/monthlyfee/upload_files/(?P<pk>[0-9]+)/$',
    #     match.MonthlyFeeClientUploadFilesView.as_view(), name='client-monthlyfee-files'),


    # Listado de matchs para el especialista
    url(r'^specialists/matchs/$',
        match.MatchListSpecialistView.as_view(),
        name='match-specialist'),
    # confirmar descuento por parte del especialista
    url(r'^confirm-discount/(?P<pk>[0-9]+)/$',
        payment.ConfirmDiscountView.as_view(),
        name='confirm-discount'),

    url(r'^backend/matchs/$',
        match.MatchBackendListView.as_view(),
        name='backend-matchs'),

    url(r'^backend/matchs/(?P<pk>[0-9]+)/$',
        match.MatchBackendDetailView.as_view(),
        name='backend-matchs-detail'),

    # Aceptar match especialista
    url(r'^specialists/accept/matchs/(?P<pk>[0-9]+)/$',
        match.MatchAcceptView.as_view(),
        name='match-specialist-accept'),

    # Declinar match especialista
    url(r'^specialists/decline/matchs/(?P<pk>[0-9]+)/$',
        match.MatchDeclineView.as_view(),
        name='match-specialist-decline'),


    # Vendedores
    url(r'^sellers/$', actors.SellerListView.as_view(), name='sellers'),
    url(r'^sellers/(?P<pk>[0-9]+)/$', actors.SellerDetailView.as_view(),
        name='seller-detail'),
    url(r'^sellers/clients/$', actors.SellerClientListView.as_view(),
        name='sellers-clients'),

    url(r'^sellers/clients/(?P<pk>[0-9]+)/assign/$', actors.AssignClientToOtherSeller.as_view(),
        name='assign-clients'),

    # Actualizar Consulta por detalle (Responder)
    url(r'^specialist/queries/(?P<pk>[0-9]+)/$',
        query.QueryDetailSpecialistView.as_view(), name='query-specialist'),

    # Contactos crear y listar en mapa
    url(r'^contacts/$', actors.ContactListView.as_view(), name='contacts'),

    # Visitas del contacto
    url(r'^visits/contacts/(?P<pk>[0-9]+)/$', actors.ContactVisitListView.as_view(), name='visits-contact'),
    # Visitas del contacto no efectiva
    url(r'^visits/noteffective/contacts/(?P<pk>[0-9]+)/$', 
        actors.ContactVisitNoEffectiveView.as_view(), name='visits-contact-noeffective'),
    # Actualizacion de visitas
    url(r'^visits/update/(?P<pk>[0-9]+)/$', 
        actors.ContactVisitUpdate.as_view(), name='visit-update'),


    # detalle de contacto
    url(r'^objections/contacts/(?P<pk>[0-9]+)/$',
        actors.ContactObjectionsDetailView.as_view(),
        name='objections-contact'),

    # filtrar contactos por efectivo, no efectivo, y fecha desde hasta
    url(r'^seller/contacts/$', actors.ContactFilterView.as_view(),
        name='contacts-filter'),
    # url para subir imagen de usuario
    url(r'^upload_photo/(?P<pk>[0-9]+)/$', actors.PhotoUploadView.as_view(),
        name='upload-photo'),
    # url para subir imagen de contacto
    url(r'^upload_photo/contact/(?P<pk>[0-9]+)/$',
        actors.PhotoContactUploadView.as_view(), name='upload-photo-contact'),

    url(r'^upload/$', actors.FileUploadView.as_view(), name='upload'),

    url(r'^upload_document/(?P<pk>[0-9]+)/$',
        actors.DocumentUploadView.as_view(), name='upload-document'),
    # cambiar clave de usuario
    url(r'^change/password/(?P<pk>[0-9]+)/$',
        actors.UpdateUserPassword.as_view(),
        name='update-password'),
    # url(r'^upload_archivo/(?P<filename>[^/]+)$', actors.AllFileUploadView.as_view())

    # chat (prueba con channels)
    url(r'^chat/$', chat.chat, name='chat'),

    # email
    url(r'^mail/$', email.mail, name='mails'),
    # Soporte
    url(r'^support/$', actors.SupportActorsView.as_view(), name='support'),

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
    # url(r'^password/(?P<pk>[0-9]+)/$', actors.UpdatePasswordView.as_view(),
    #     name='update-pass'),

    # Compras
    url(r'^purchase/$',
        purchase.CreatePurchase.as_view(), name='purchase'),

    url(r'^contact/purchase/$',
        purchase.ContactNoEffectivePurchase.as_view(), name='contact-purchase'),

    url(r'^purchase/(?P<pk>[0-9]+)/$',
        purchase.PurchaseDetail.as_view(), name='purchase-detail'),

    # Pagos
    url(r'^payment/$',
        payment.CreatePayment.as_view(), name='payment'),
    # Pago de especialista match
    url(r'^specialists/payment/match/$',
        payment.MatchPaymentSpecialist.as_view(),
        name='payment-match-specialist'),
    # Pago de Match Cliente
    url(r'^clients/payment/match/$',
        payment.MatchPaymentClient.as_view(),
        name='payment-match-client'),

    url(r'^sales/payment-pending/$',
        payment.PaymentPendingView.as_view(), name='sale-payment-pending'),

    url(r'^fees/payment-pending/(?P<pk>[0-9]+)/$',
        payment.PaymentPendingDetailView.as_view(),
        name='fee-payment-pending-detail'),

    url(r'^fees/payment-pending-by-client/$',
        payment.PaymentDetailContactView.as_view(), name='payment-pending-by-client-detail'),

    url(r'^clients/sales/have-payment-pending/$',
        payment.ClientHaveSalePending.as_view(), name='payment-pending-sale-client'),

    url(r'^clients/sales/detail/(?P<sale_id>[0-9]+)/$',
        payment.ClientSaleDetail.as_view(), name='payment-sale-client'),

    url(r'^pending/data/$',
        notification.PendingNotificationView.as_view(), name='get-badge'),
]
