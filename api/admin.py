"""Se registran los modelos para facilitar pruebas y visualziacion directa."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, User, Seller, Client, Category, Specialist, Query,Quota,Seller,Zone
from .models import Department, Province, District, Message, MessageFile, Plan, Product
from .models import Purchase, PaymentType, Fee, Objection
# Register your models here.



class ClientNaturalAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name',
     'sex', 'civil_state','birthdate',
     'level_instruction', 'institute','profession',
     'ocupation')

class ClientBussinessAdmin(admin.ModelAdmin):
    fields  = (
     'economic_sector',
     'agent_firstname', 'agent_lastname',
     'position','business_name')

class ClientBase(admin.ModelAdmin):
    """
        Esta clase integra todos los campos de usuario, cliente
        Natural y Cliente Juridico, las validaciones correspondientes
        deben hacerse a juicio propio, segun los comportamientos de
        linkup, ejemplo: RUC es requerido si el usuario es Peruano
    """
    fields = ('username','nick','password','photo',
     'document_type','nationality','ruc',
     'document_number','email_exact','code','telephone', 'cellphone','ciiu',
     'activity_description','about','anonymous','role','type_client','status'
     'first_name', 'last_name',
     'sex', 'civil_state','birthdate',
     'level_instruction', 'institute','profession',
     'ocupation',
     'business_name','economic_sector','agent_firstname', 'agent_lastname',
     'position','seller_asigned')

class SpecialistAdmin(admin.ModelAdmin):
    fields = ('username', 'nick','password','photo','first_name', 'last_name',
    'business_name','type_specialist','email_exact','telephone',
    'cellphone','document_type', 'document_number',
    'ruc','code','payment_per_answer','anonymous','role','category','status')

class MessageFileInline(admin.TabularInline):
    model = MessageFile
    extra = 1

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

class MessageAdmin(admin.ModelAdmin):
    inlines = [MessageFileInline]
    list_display = ('message','msg_type','created_at')

class QueryAdmin(admin.ModelAdmin):
    inlines = [MessageInline]
    readonly_fields = ('calification',)

class SellerAdmin(admin.ModelAdmin):
    fields = ('zone','username', 'nick','password','first_name', 'last_name',
    'email_exact','telephone','cellphone','document_type','code', 'document_number',
    'ruc','status')

class PlanAdmin(admin.ModelAdmin):
    fields = ('name',)

class PurchaseAdmin(admin.ModelAdmin):
    fields = ('client','seller','total_amount','reference_number','fee_number','latitude','longitude','query_available',
        'is_promotional','last_number_fee_paid','status','expiration_date','promotion','code','product','query_amount')


admin.site.register(Client, ClientNaturalAdmin)
# admin.site.register(Client,ClientBussinessAdmin)
admin.site.register(Category)
admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Department)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Quota)
admin.site.register(Zone)
admin.site.register(Objection)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(PaymentType)
admin.site.register(Fee)
