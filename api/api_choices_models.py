from django.utils.translation import ugettext_lazy as _

class ChoicesAPI:
    """
        Clase Choices para manejo de opciones en los modelos
        cada atributo de la clase es una opcion de modelo
        la estructura en los nombres de los choises es la siguiente
        nombre del modelo + piso + nombre de atributo
        e.g: "client_type_client" o "client_sex"
    """

    # User Model
    user_document_type = (
        (1, _('DNI')),
        (2, _('Passport')),
        (3, _('Foreign Card')),
    )

    user_status = (
        (1, _('Pending')),
        (2, _('Activate')),
        (3, _('Reject')),
        (4, _('Deactivated')),
    )

    # Client Model
    client_type_client = (
        ('n', _('Natural')),
        ('b', _('Business')),
    )

    client_full_type_client = (
        ('n', _('Natural Person')),
        ('b', _('Business Person')),
    )

    client_sex = (
        ('m', _('Male')),
        ('f', _('Female')),
    )

    client_civil_state = (
        ('c', _('cohabiting')),
        ('e', _('separated')),
        ('m', _('married')),
        ('w', _('widower')),
        ('d', _('divorced')),
        ('s', _('single')),
    )

    client_ocupation = (
        (1, _('Employer')),
        (2, _('Independent worker')),
        (3, _('Employee')),
        (4, _('Worker')),
        (5, _('Worker in a family business')),
        (6, _('Home worker')),
        (7, _('Other')),
    )

    # Specialist Model
    specialist_type_specialist = (
        ('m', _('Main')),
        ('a', _('Associate')),
    )

    # Specialistcontract Model
    specialistcontract_state = (
        ('r', _('Requested')),
        ('a', _('Accepted')),
        ('d', _('Declined')),
    )

    # Promotion Model
    promotions_type = (
        ('p', _('Percentage')),
        ('n', _('Number')),
    )

    # Purchase Model
    fee_status = (
        (1, _('Pending')),
        (2, _('Paid')),
        (3, _('Checking payment')),
    )
    # venta estado
    sale_status = (
        (1, _('Unpaid')),  # no se ha pagado
        (2, _('Progress')),  # al menos una cuota la pagaron
        (3, _('Paid')),  # ya se pago
    )

    # CulqiPayment Model
    culqipayment_status = (
        ('w', _('Wait')),
        ('d', _('Denied')),
        ('e', _('Exhaled')),
        ('p', _('Paid')),
    )

    # payment model
    payment_status = (
        (1, _('Pending')),
        (2, _('Accepted')),
        (3, _('Declined')),
    )

    # Query Model
    query_status = (
        (1, _('Requested')),  # pendiente por derivar, responder o declinar
        (2, _('Accepted')),  # consulta aceptada por un especialista
        (3, _('Answered')),  # respondida por especialista
        (4, _('To score')),  # pendiente por puntuar
        (5, _('Absolved')),  # resuelta y finalizada
    )

    # Plan Estado
    plan_status = (
        (1, _('Reserved')),  # reservado, pendiente de pago
        (2, _('Pending Confirmation')),  # reporte pago, esperando confirmacion
        (3, _('Insert Your Pin')),  # confirmado pago, falta por activar
        (4, _('In Use')),  # Activo
        (5, _('Culminated')),  # expirado o finalidas las consultas
    )
    # MatchAcquired model
    match_acquired_status = (
        (1, _('Requested')),  # solicitado
        (2, _('Accepted')),  # aceptado por especialista, falta que pague el especialista
        (3, _('Declined')),  # declinado por especialista
        (4, _('Pending paid client')),  # Pendiente pago del usuario. sino es cliente
        (5, _('Done')),  # hecho, match exitoso
        (6, _('Voucher uploaded')),  # ya se subio el voucher de cliente
    )

    match_paid_specialist = (
        (1, _('paid_bank')),
        (2, _('make_discount'))
    )

    # Message Model
    message_msg_type = (
        ('q', _('query')),  # es de tipo consulta
        ('r', _('requery')),  # es de tipo reconsulta
        ('a', _('answer')),  # es de tipo respuesta
    )

   # Para mensaje y Match
    message_content_type = (
        (1, _('Text')),
        (2, _('Image')),
        (3, _('Video')),
        (4, _('Voice')),
        (5, _('Document')),
    )

    # AlertCategory Model
    alertcategory_name = (
        ('c', _('Critic')),
        ('m', _('Moderate')),
        ('p', _('Positive')),
    )

    # Query Plan Client
    queryplansclient_status = (
        (1, _('Active')),
        (2, _('Deactivated')),
    )

    # Query Plan Manage
    queryplansmanage_type_operation = (
        (1, _('Transfer')),
        (2, _('Share')),
        (3, _('Empower')),
    )
    queryplansmanage_status = (
        (1, _('Active')),
        (2, _('Deactivated')),
        (3, _('Processing')),
    )

    file_status = (
        (0, _('Loaded')),
        (1, _('Sent')),
        (2, _('Delivered')),
        (3, _('Read')),
        (4, _('Failed')),
    )
    # tipo de Contacto
    type_seller_contact = (
        (1, _('Effective')),
        (2, _('Non Effective')),
        (3, _('Effective paid')),  # efectivo que ya ha pagado.
        (4, _('Promotional')),
    )
