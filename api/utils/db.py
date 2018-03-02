import os, sys
from subprocess import check_output
import MySQLdb

BASE_PROYECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_PROYECT)  # Nos ubicamos en la raiz del proyecto
from linkupapi.settings_secret import DATABASES

db = MySQLdb.connect(host=DATABASES['default']['HOST'],  # tu host, usualmente localhost
                     user=DATABASES['default']['USER'],  # tu usuario
                     passwd=DATABASES['default']['PASSWORD'],  # tu password
                     db=DATABASES['default']['NAME'])  # el nombre de la base de datos

cur = db.cursor()
cur.execute("SHOW TABLES WHERE Tables_in_linkup REGEXP 'oauth2_provider_accesstoken|api_'")

path = path2 = ""
list_names = []
exit = True
if 'api' in os.listdir("."):
    path2 = "api\\fixtures\\temp\\"
elif 'db.py' in os.listdir("."):
    path = "..\\..\\"
    path2 = "..\\fixtures\\temp\\"

tables_db = [row[0].replace("api_", "").replace("oauth2_provider_", "") for row in cur.fetchall()]
while True:
    print("Nombre de la tabla: ")
    table_name = input()
    if table_name.lower().strip() == "exit":
        exit = False
        break
    if table_name.strip() != "":
        if table_name.strip() == ".":
            break
        if table_name.lower().strip() == "all":
            list_names = tables_db
            break
        if "," in table_name:
            list_names = [x.strip() for x in table_name.split(',') if x.strip() != ""]
            z = list(set(list_names) - set(tables_db))
            if len(z) > 0:
                print("Las siguientes tablas no existen en la base de datos: {}".format(z))
                continue
            else:
                break
        if table_name.lower().strip() in tables_db:
            list_names.append(table_name)
        else:
            print("La tabla {} no existe".format(table_name))

if exit:
    print("Nombre del fixture: ")
    name_fixture = input()
    list_prefix = [" api." + name for name in list_names if name != "accesstoken"]
    result = ''.join(str(e) for e in list_prefix)
    # se agregan dos tablas necesarias
    result += " oauth2_provider.accesstoken oauth2_provider.application"
    check_output(r"python {}manage.py dumpdata {} --indent 2 > {}{}.json".format(path, result, path2, name_fixture),
                 shell=True).decode()
cur.close()
db.close()
