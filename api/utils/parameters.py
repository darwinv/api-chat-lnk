class Params:
    """
        Clase de parametros generales
    """
    # prefijos para usuarios y listas
    PREFIX = {
        "client": "u",
        "specialist": "s",
        "seller": "sl",
        "category": "c",
        "query": "q",
        "message": "m"
    }
    CODE_PREFIX = {
        "client": "C",
        "specialist": "E",
        "specialist_associate": "EA",
        "seller": "V"
    }
    ROLE_CLIENT = 2

    TIME_ZONE = ""
    
class Payloads:
    read = True
    categoriesList = {
        "c1": {
            "datetime": "",
            "id": 1,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-02.png",
            "name": "Impuestos",
            "read": read
        }, "c2": {
            "datetime": "",
            "id": 2,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-03.png",
            "name": "Contabilidad",
            "read": read
        }, "c3": {
            "datetime": "",
            "id": 3,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-17.png",
            "name": "Derecho Tributario",
            "read": read
        }, "c4": {
            "datetime": "",
            "id": 4,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-04.png",
            "name": "Finanzas",
            "read": read
        }, "c5": {
            "datetime": "",
            "id": 5,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-05.png",
            "name": "Seguros",
            "read": read
        }, "c6": {
            "datetime": "",
            "id": 6,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-10.png",
            "name": "Derecho Corporativo",
            "read": read
        }, "c7": {
            "datetime": "",
            "id": 7,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-06.png",
            "name": "Comercio Exterior",
            "read": read
        }, "c8": {
            "datetime": "",
            "id": 8,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-08.png",
            "name": "Tecnología de la Información",
            "read": read
        }, "c9": {
            "datetime": "",
            "id": 9,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-17-2.png",
            "name": "Propiedad Intelectual",
            "read": read
        }, "c10": {
            "datetime": "",
            "id": 10,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-07.png",
            "name": "Publicidad",
            "read": read
        }, "c11": {
            "datetime": "",
            "id": 11,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-09.png",
            "name": "Psicología Organizacional",
            "read": read
        }, "c12": {
            "datetime": "",
            "id": 12,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-24.png",
            "name": "Contrataciones con el Estado",
            "read": read
        }, "c13": {
            "datetime": "",
            "id": 13,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-29-1.png",
            "name": "Marketing",
            "read": read
        }, "c14": {
            "datetime": "",
            "id": 14,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-24-1.png",
            "name": "Mecánica",
            "read": read
        }, "c15": {
            "datetime": "",
            "id": 15,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-16.png",
            "name": "Derecho Notarial y Registral",
            "read": read
        }, "c16": {
            "datetime": "",
            "id": 16,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-30-1.png",
            "name": "Gestión de Proyectos",
            "read": read
        }, "c17": {
            "datetime": "",
            "id": 17,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-20-1.png",
            "name": "Electricidad",
            "read": read
        }, "c18": {
            "datetime": "",
            "id": 18,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-12.png",
            "name": "Derecho Procesal Civil",
            "read": read
        }, "c19": {
            "datetime": "",
            "id": 19,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-21-3.png",
            "name": "Agroindustria",
            "read": read
        }, "c20": {
            "datetime": "",
            "id": 20,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-22-1.png",
            "name": "Electrónica",
            "read": read
        }, "c21": {
            "datetime": "",
            "id": 21,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-14.png",
            "name": "Derecho Penal",
            "read": read
        }, "c22": {
            "datetime": "",
            "id": 22,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-27.png",
            "name": "Alimentaria",
            "read": read
        }, "c23": {
            "datetime": "",
            "id": 23,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-23-2.png",
            "name": "Automatización",
            "read": read
        }, "c24": {
            "datetime": "",
            "id": 24,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-11.png",
            "name": "Derecho Laboral",
            "read": read
        }, "c25": {
            "datetime": "",
            "id": 25,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-28-2.png",
            "name": "Gastronomía",
            "read": read
        }, "c26": {
            "datetime": "",
            "id": 26,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-26.png",
            "name": "Plásticos",
            "read": read
        }, "c27": {
            "datetime": "",
            "id": 27,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-15.png",
            "name": "Derecho Minero",
            "read": read
        }
    }
