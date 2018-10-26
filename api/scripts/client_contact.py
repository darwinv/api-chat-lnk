
from api.models import Client, SellerContact, Sale
import pdb

def get_data(client):
    """Devuelve data que servira para crear un contacto a partir de un cliente"""

    type_contact = 3 if Sale.objects.filter(client=client.id, status__range=(2, 3)) else 1
    data = {
            'first_name': client.first_name,
            'last_name': client.last_name,
            'type_contact': type_contact,
            'type_client': client.type_client,
            'civil_state': client.civil_state,
            'birthdate': client.birthdate,
            "address": client.address,
            'sex': client.sex,
            'document_type': client.document_type,
            'document_number': client.document_number,
            'email_exact': client.email_exact,
            'telephone': client.telephone,
            'cellphone': client.cellphone,
            'activity_description': client.activity_description,
            'level_instruction': client.level_instruction,
            'institute': client.institute,
            'profession': client.profession,
            'ocupation': client.ocupation,
            "latitude": "-77.0282400",
            "longitude": "-12.0431800",
            'about': client.about,
            'seller': client.seller_assigned,
            'nationality': client.nationality,
            'residence_country': client.residence_country
        }

    return data

def sync():
    """
    Todos los clientes tienen una instancia de contacto con los mismos datos
    Esta funcion los sincroniza o los crea, de ser necesario
    """

    # Primero se agregan clientes a los contactos ya existentes
    clients = Client.objects.all()
    contacts = SellerContact.objects.filter(email_exact__in=clients.values('email_exact'))

    for contact in contacts:
        if contact.client is None:
            client = Client.objects.get(email_exact=contact.email_exact)
            contact.client = client
            contact.save()

    # Luego se crean contactos nuevos para conectarse con los clientes
    clients = Client.objects.exclude(email_exact__in=contacts.values('email_exact'))

    contact =  None
    for client in clients:
        contact = SellerContact(**get_data(client))
        contact.client = client
        contact.save()

def change_contact_type():
    """
    Cambia el tipo de contacto de 2 a 1 si es que son clientes
    """

    clients = Client.objects.exclude(status__range=(2, 3))
    SellerContact.objects.filter(client__in=clients, type_contact=2).update(type_contact=1)
