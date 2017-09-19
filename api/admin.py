from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, User, Seller, Client
# Register your models here.

class ClientNaturalAdmin(admin.ModelAdmin):
    # exclude = ('updated_at', 'email_exact')
    fields = ('username','nick','password','photo','first_name', 'last_name',
     'type_client', 'sex', 'civil_state','birthdate', 'document_type',
     'document_number','email_exact','code','telephone', 'cellphone','ciiu',
     'activity_description','level_instruction', 'institute','profession',
     'ocupation', 'about','anonymous','role','nationality')

admin.site.register(Client,ClientNaturalAdmin)
