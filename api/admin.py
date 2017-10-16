from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, User, Seller, Client, Category, Specialist, Query, Answer, Quota
from .models import Department, Province, District
# Register your models here.

class ClientNaturalAdmin(admin.ModelAdmin):
    fields = ('username','nick','password','photo','first_name', 'last_name',
     'type_client', 'sex', 'civil_state','birthdate', 'document_type',
     'document_number','email_exact','code','telephone', 'cellphone','ciiu',
     'activity_description','level_instruction', 'institute','profession',
     'ocupation', 'about','anonymous','role','nationality')

class ClientBussinessAdmin(admin.ModelAdmin):
    fields  = ('username','nick','password','photo','business_name',
     'type_client', 'document_type', 'document_number', 'email_exact',
     'code','telephone', 'cellphone', 'commercial_group', 'economic_sector',
     'ciiu', 'activity_description','agent_firstname', 'agent_lastname',
     'position','about','anonymous','role','nationality')

class SpecialistAdmin(admin.ModelAdmin):
    fields = ('username', 'nick','password','photo','first_name', 'last_name',
    'business_name','type_specialist','email_exact','telephone',
    'cellphone','document_type', 'document_number',
    'ruc','code','payment_per_answer','anonymous','role','category')

class QueryAdmin(admin.ModelAdmin):
    exclude = ('declined_motive',)

admin.site.register(Client,ClientNaturalAdmin)
# admin.site.register(Client,ClientBussinessAdmin)
admin.site.register(Category)
admin.site.register(Specialist,SpecialistAdmin)
admin.site.register(Query,QueryAdmin)
admin.site.register(Answer)
admin.site.register(Department)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Quota)
