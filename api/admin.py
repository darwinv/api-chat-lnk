"""Se registran los modelos para facilitar pruebas y visualziacion directa."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from .models import Role, User, Seller, Client, Category, Specialist, Query, Zone
# from .models import Department, Province, District, Message, MessageFile
# from .models import PaymentType, Objection
# from .models import QueryPlans, QueryPlansAcquired, Clasification
# from .models import SaleDetail, Sale
# from .models import ContractType, Contract
from .models import Countries, Ciiu, Department, Province, District, Address, Zone
from .models import Permmission, Role, User, Seller, Objection, EconomicSector, LevelInstruction
from .models import SellerContactNoEfective, Client, ContractType, Contract, Category, Bank, Specialist
from .models import Clasification, ProductType, QueryPlans, SellerNonBillablePlans, Match, Sale
from .models import SaleDetail, QueryPlansAcquired, PaymentType, Payment, MatchAcquired
from .models import MatchAcquiredFiles, MatchAcquiredLog, MonthlyFee, LogPaymentsCreditCard
from .models import Query, QueryLogs, Message, FeeMonthSeller, NotificationsBack
from .models import Parameter
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
     'activity_description','about','anonymous','role','type_client','status',
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


class MessageInline(admin.TabularInline):
    """Mensaje en Linea."""

    model = Message
    extra = 1


class MessageAdmin(admin.ModelAdmin):
    """Registro en el admin de Mensaje."""

    list_display = ('message', 'msg_type', 'created_at')


class QueryAdmin(admin.ModelAdmin):
    """Consulta en el admin."""

    inlines = [MessageInline]
    readonly_fields = ('calification',)
    exclude = ('acq3uired_plan',)

class SellerAdmin(admin.ModelAdmin):
    fields = ('zone','username', 'nick','password','first_name', 'last_name',
    'email_exact','telephone','cellphone','document_type','code', 'document_number',
    'ruc','status')


admin.site.register(Client, ClientBase)
# admin.site.register(Client,ClientBussinessAdmin)
admin.site.register(Category)
admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Department)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Zone)
admin.site.register(Objection)
admin.site.register(Seller, SellerAdmin)
admin.site.register(PaymentType)
admin.site.register(QueryPlans)
admin.site.register(QueryPlansAcquired)
admin.site.register(Clasification)
admin.site.register(SaleDetail)
admin.site.register(Sale)
admin.site.register(ContractType)
admin.site.register(Contract)


# Modelos para modificacion de pruebas
admin.site.register(Countries)
admin.site.register(Ciiu)
admin.site.register(Address)

admin.site.register(Permmission)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(EconomicSector)
admin.site.register(LevelInstruction)

admin.site.register(SellerContactNoEfective)
admin.site.register(Bank)

admin.site.register(ProductType)
admin.site.register(SellerNonBillablePlans)
admin.site.register(Match)

admin.site.register(Payment)
admin.site.register(MatchAcquired)

admin.site.register(MatchAcquiredFiles)
admin.site.register(MatchAcquiredLog)
admin.site.register(MonthlyFee)
admin.site.register(LogPaymentsCreditCard)

admin.site.register(QueryLogs)
admin.site.register(FeeMonthSeller)
admin.site.register(NotificationsBack)

admin.site.register(Parameter)
