from api.models import ContactVisit, SellerContact, ObjectionsList, Sale

def update_visits():
    """
    generar las visitas
    """

    for contact in SellerContact.objects.all():

        if contact.type_contact != 2:
            for sale in Sale.objects.filter(client=contact.client):
                
                type_contact = contact.type_contact
                if type_contact == 3:
                    type_contact = 1

                visit = ContactVisit.objects.create(contact=contact,
                                        type_visit=type_contact,
                                        latitude=contact.latitude,
                                        longitude=contact.longitude,
                                        sale=sale,
                                        seller=contact.seller)

                
        else:
            visit = ContactVisit.objects.create(contact=contact,
                                        type_visit=contact.type_contact,
                                        latitude=contact.latitude,
                                        longitude=contact.longitude,
                                        other_objection=contact.other_objection,
                                        seller=contact.seller)
        
            objections = ObjectionsList.objects.filter(contact=contact)

            if objections:
                objections.update(contact_visit=visit)
            else:
                visit.other_objection = "Tengo que pensar un poco mejor la oferta"
                visit.save()

