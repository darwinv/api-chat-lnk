class Params:
    """
        Clase de parametros generales
    """
    # prefijos para usuarios y listas
    PREFIX = {
        "client": "u",
        "specialist": "sp",
        "seller": "se",
        "category": "c"
    }


class Payloads:
    categoriesList = {
        "1": {
            "datetime": "2018-03-31 12:52:10.742779",
            "id": 1,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-02.png",
            "name": "Impuestos"
        }, "2": {
            "datetime": "2018-02-05 12:52:10.742769",
            "id": 2,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-03.png",
            "name": "Contabilidad"
        }, "3": {
            "datetime": "2018-03-07 12:52:10.742789",
            "id": 3,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-17.png",
            "name": "Derecho Tributario"
        }, "4": {
            "datetime": "2018-03-08 12:52:10.742789",
            "id": 4,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-04.png",
            "name": "Finanzas"
        }, "5": {
            "datetime": "2018-03-09 12:52:10.742789",
            "id": 5,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-05.png",
            "name": "Seguros"
        }, "6": {
            "datetime": "2018-03-10 12:52:10.742789",
            "id": 6,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-10.png",
            "name": "Derecho Corporativo"
        }, "7": {
            "datetime": "2018-03-11 12:52:10.742789",
            "id": 7,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-06.png",
            "name": "Comercio Exterior"
        }, "8": {
            "datetime": "2018-03-12 12:52:10.742789",
            "id": 8,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-08.png",
            "name": "Tecnología de la Información"
        }, "9": {
            "datetime": "2018-03-13 12:52:10.742789",
            "id": 9,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-17-2.png",
            "name": "Propiedad Intelectual"
        }, "10": {
            "datetime": "2018-03-14 12:52:10.742789",
            "id": 10,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-07.png",
            "name": "Publicidad"
        }, "11": {
            "datetime": "2018-03-15 12:52:10.742789",
            "id": 11,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-09.png",
            "name": "Psicología Organizacional"
        }, "12": {
            "datetime": "2018-03-16 12:52:10.742789",
            "id": 12,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-24.png",
            "name": "Contrataciones con el Estado"
        }, "13": {
            "datetime": "2018-03-17 12:52:10.742789",
            "id": 13,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-29-1.png",
            "name": "Marketing"
        }, "14": {
            "datetime": "2018-03-18 12:52:10.742789",
            "id": 14,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-24-1.png",
            "name": "Mecánica"
        }, "15": {
            "datetime": "2018-03-19 12:52:10.742789",
            "id": 15,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-16.png",
            "name": "Derecho Notarial y Registral"
        }, "16": {
            "datetime": "2018-03-20 12:52:10.742789",
            "id": 16,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-30-1.png",
            "name": "Gestión de Proyectos"
        }, "17": {
            "datetime": "2018-03-21 12:52:10.742789",
            "id": 17,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-20-1.png",
            "name": "Electricidad"
        }, "18": {
            "datetime": "2018-03-22 12:52:10.742789",
            "id": 18,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-12.png",
            "name": "Derecho Procesal Civil"
        }, "19": {
            "datetime": "2018-03-23 12:52:10.742789",
            "id": 19,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-21-3.png",
            "name": "Agroindustria"
        }, "20": {
            "datetime": "2018-03-24 12:52:10.742789",
            "id": 20,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-22-1.png",
            "name": "Electronics"
        }, "21": {
            "datetime": "2018-03-25 12:52:10.742789",
            "id": 21,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-14.png",
            "name": "Derecho Penal"
        }, "22": {
            "datetime": "2018-03-26 12:52:10.742789",
            "id": 22,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-27.png",
            "name": "Alimentaria"
        }, "23": {
            "datetime": "2018-03-27 12:52:10.742789",
            "id": 23,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-23-2.png",
            "name": "Automatización"
        }, "24": {
            "datetime": "2018-03-28 12:52:10.742789",
            "id": 24,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-11.png",
            "name": "Derecho Laboral"
        }, "25": {
            "datetime": "2018-03-29 12:52:10.742789",
            "id": 25,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-28-2.png",
            "name": "Gastronomía"
        }, "26": {
            "datetime": "2018-03-30 12:52:10.742789",
            "id": 26,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-26.png",
            "name": "Plásticos"
        }, "27": {
            "datetime": "2018-03-31 12:52:10.742789",
            "id": 27,
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-15.png",
            "name": "Derecho Minero"
        }
    }
