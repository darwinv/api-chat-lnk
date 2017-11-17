
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
        ('0', 'DNI'),
        ('1', 'Passport'),
        ('2', 'Foreign Card'),
    )

    # Client Model
    client_type_client = (
            ('n', _('Natural')),
            ('b', _('Bussiness')),
        )

    client_sex = (
            ('n', _('Male')),
            ('b', _('Female')),
        )
    client_civil_state = (
        ('c','cohabiting'),
        ('e','separated'),
        ('m','married'),
        ('w','widower'),
        ('d','divorced'),
        ('s','single'),
    )

    client_ocupation = (
    ('0','Employer'),
    ('1','Independent worker'),
    ('2','Employee'),
    ('3','Worker'),
    ('4','Worker in a family business'),
    ('5','Home worker'),
    ('6','Other'),
    )

    # Specialist Model
    specialist_type_specialist = (
        ('m', 'Main'),
        ('a', 'Associate'),
    )

    # Specialistcontract Model
    specialistcontract_state = (
        ('r', 'Requested'),
        ('a', 'Accepted'),
        ('d', 'Declined'),
    )

    # Promotion Model
    promotions_type = (
        ('p', 'Percentage'),
        ('n', 'Number'),
    )


    # Purchase Model
    purchase_status = (
        ('0', 'Pending'),
        ('1', 'Paid'),
    )

