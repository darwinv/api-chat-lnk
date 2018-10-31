
from api.models import Client, SellerContact, Sale
import pdb

def get_data(client):
    """Devuelve data que servira para crear un contacto a partir de un cliente"""

    fields = ['first_name', 'last_name', 'type_client', 'civil_state', 'birthdate', "address", 'sex',
            'document_type', 'document_number', 'email_exact', 'telephone', 'cellphone', 'activity_description',
            'level_instruction', 'institute', 'profession', 'ocupation', "latitude", "longitude", 'about',
            'nationality', 'residence_country', 'ciiu', 'photo', 'code_telephone', 'code_cellphone', 'business_name',
            'commercial_reason', 'agent_firstname', 'agent_lastname', 'position', 'ruc', 'economic_sector',
            'foreign_address']

    data = {}

    for field in fields:
        data[field] = getattr(client, field) if hasattr(client, field) else None
    

    data['type_contact'] = 3 if Sale.objects.filter(client=client.id, status__range=(2, 3)) else 1
    data['seller'] = client.seller_assigned
    data['latitude'] = '-77.0282400'
    data['longitude'] = '-12.0431800'

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
        data = get_data(client)
        contact = SellerContact.objects.create(**data)
        contact.client = client
        contact.save()

def change_contact_type():
    """
    Cambia el tipo de contacto de 2 a 1 si es que son clientes
    """

    clients = Client.objects.exclude(status__range=(2, 3))
    SellerContact.objects.filter(client__in=clients, type_contact=2).update(type_contact=1)
