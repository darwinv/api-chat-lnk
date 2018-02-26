# import os, sys
#import subprocess
from subprocess import check_output
import MySQLdb
# from django.conf import settings
# from api.config import
# import sys
# sys.path.append("../linkup/")
# # import setting_secret
#
# lib_path = os.path.abspath(os.path.join('..', 'linkup'))
# sys.path.append(lib_path)
#
# print()
# settings.configure(DEBUG=True)
# ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"
# pl = settings.DATABASES
# print(pl)
# DATABASES = getattr(settings, "DATABASES", None)
# for i in DATABASES:
# 	print(i)
# print (getattr(settings, "DATABASES", None))
#import re
#proj_path =r"C:\Users\marko\PycharmProjects\linkupapi"
# proj_path ="."
# This is so Django knows where to find stuff.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "linkupapi.settings")

# sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
# os.chdir(proj_path)

# This is so models get loaded.
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

#subprocess.call(["python ","manage.py","dumpdata","api.Contract","--indent","2",">","Contracts.json"])
db = MySQLdb.connect(host="localhost",    # tu host, usualmente localhost
                     user="root",         # tu usuario
                     passwd="",  # tu password
                     db="api_linkup")        # el nombre de la base de datos

# Debes crear un objeto Cursor. Te permitirá
# ejecutar todos los queries que necesitas
cur = db.cursor()
# Usa todas las sentencias SQL que quieras
cur.execute("SHOW TABLES")
aux_api = []
aux_auth = []
aux_oauth2 = []
for row in cur.fetchall():
	if not row[0].find("api_"):
		aux_api.append(row[0].replace("api_", ""))
	elif not row[0].find("oauth2_"):
		aux_oauth2.append(row[0].replace("oauth2_provider_", ""))
# print(aux_api)
# print(aux_oauth2)

px = [" oauth2_provider." + name for name in aux_oauth2]
fx = ''.join(str(e) for e in px)
# print(fx)
# oauth2_provider.
list_name = []
filenames = []
tables_db = aux_api

# print(tables_db)

con = 0
aux = 0
name_fixture = ""
while True:
	print ("Nombre de la tabla: ")
	table_name = input()
	if table_name.strip() != "":
		if table_name.strip() == ".":
			break
		if table_name.lower().strip() == "all":
			list_name = tables_db
			break
		if table_name.lower().strip() in tables_db:
			list_name.append(table_name)
		else:
			print("La tabla {} no existe".format(table_name))

print("Nombre del fixture: ")
name_fixture = input()

e = ""
p = [" api." + name for name in list_name]
f = ''.join(str(e) for e in p)
check_output(r"python ..\..\manage.py dumpdata {} --indent 2 > ..\fixtures\temp\{}.json".format(f, name_fixture), shell=True).decode()
check_output(r"python ..\..\manage.py dumpdata {} --indent 2 > ..\fixtures\temp\{}.json".format(fx, name_fixture + "_oauth2"), shell=True).decode()

# for name in list_name:
# 	filenames.append(r"api\fixtures\temp\{}.json".format(name))
# 	check_output(r"python manage.py dumpdata api.{} --indent 2 > api\fixtures\temp\{}.json".format(name, name), shell=True).decode()
#
# with open(r"api\fixtures\temp\{}.json".format(name_fixture), 'w') as outfile:
# 	outfile.write('[\n')
# 	for fname in filenames:
# 		with open(fname) as infile:
# 			aux = 0
# 			for line in infile:
# 				outfile.write(line.replace("[","").replace("]",""))
# 			con += 1
# 			if con < len(filenames):
# 				outfile.write(',\n')
# 	outfile.write(']\n')
#
# with open(r"api\fixtures\temp\{}.json".format(name_fixture)) as input_file, open(r"api\fixtures\temp\_.json", 'w') as output_file:
# 	for line in input_file:
# 		if line == ',\n':
# 			output_file.write('\n')
# 		else:
# 			output_file.write(line)
cur.close()
db.close()
