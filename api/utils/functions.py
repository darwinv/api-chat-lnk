"""Funciones utiles para logica de negocio"""
from api.models import Parameter, ParameterSeller, Seller, QueryPlansManage
import datetime

def generate_sellers_goals():
    """Genera los goals de los vendedores que todavia no tengan metas para este mes"""
    today = datetime.datetime.now()
    number_month = today.month
    number_year = today.year
    
    sellers = Seller.objects.raw("SELECT api_seller.user_ptr_id FROM api_seller WHERE \
        ( SELECT api_parameterseller.seller_id FROM \
        api_parameterseller WHERE api_parameterseller.seller_id = api_seller.user_ptr_id AND \
        api_parameterseller.number_month = {m} AND api_parameterseller.number_year = {y})\
        IS NULL".format(m=number_month, y=number_year))

    for seller in sellers:
        generate_seller_goals(seller.id)

def generate_seller_goals(seller_id, day=None):
    """Generar los goals de un vendedor"""
    contacts_goal = Parameter.objects.get(parameter="contacts_goal")
    new_clients_goal = Parameter.objects.get(parameter="new_clients_goal")
    people_purchase_goal = Parameter.objects.get(parameter="people_purchase_goal")

    seller = Seller.objects.get(pk=seller_id)

    if not day:
        day = datetime.datetime.now()

    number_month = day.month
    number_year = day.year

    ParameterSeller.objects.create(
                        contacts_goal = contacts_goal.value,
                        new_clients_goal = new_clients_goal.value,
                        people_purchase_goal = people_purchase_goal.value,
                        seller = seller,
                        number_month = number_month,
                        number_year = number_year)



def generate_message_code_user(client, acquired_plan):
    """
        client: Objeto cliente
        acquired_plan: Objeto acquired_plan
        retorna string para cada mensaje de la consulta
        return str 
    """
    document_number = role = prefix = ""
    
    if client.type_client=="b":
        document_number = client.ruc     
    else:
        document_number = client.document_number

    if acquired_plan.sale_detail.is_billable:
        role = "C"
    else:
        role = "U"

    ManageObj = QueryPlansManage.objects.filter(receiver=client, acquired_plan=acquired_plan)
    if ManageObj:
        if ManageObj[0].type_operation == 1:
            prefix = 'T'
        if ManageObj[0].type_operation == 3:
            prefix = 'F'
    else:
        ManageObj = QueryPlansManage.objects.filter(receiver=client, new_acquired_plan=acquired_plan)
        if ManageObj and ManageObj[0].type_operation == 2:
            prefix = 'C'

    code_user = role + prefix + document_number

    return code_user