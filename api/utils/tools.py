## Archivo Tools para crear funciones de sistema generar que seran reutilizadas
# A lo largo del proyecto Linkup
import datetime

def get_date_by_time(validity_months):
	"""
	funcion creada para calcular la fecha, segun cantidad en meses dada
	( 1 mes son 30 dias)
	:param validity_months: Numero entero en meses
	:return: datetime.date
	"""
	return datetime.date.today() + datetime.timedelta(validity_months*365/12)