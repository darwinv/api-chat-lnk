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
    # Tipo de notificacion (para push notif)
    TYPE_NOTIF = {
        "default": 0,
        "browsable": 1,
        "query_new": 2,
        "query_requery": 3,
        "query_declined": 4,
        "query_derived": 5,
        "query_answer": 6,
        "match_new": 7,
        "match_declined": 8,
        "match_success": 9,
        "plan": 10,
        "PIN": 11
     }

    CODE_PREFIX = {
        "client": "C",
        "specialist": "E",
        "specialist_associate": "EA",
        "seller": "V"
    }
    ROLE_CLIENT = 2
    ROLE_SPECIALIST = 3
    ROLE_SELLER = 4

    TIME_ZONE = ""


class Payloads:
    read = True
    categoriesList = {
        "c1":{ 
            "id": 1,
            "read": True,
            "status": 1,
            "order": 1,
            "name": "Taxes",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-02.png",
            "description": "actividad economica que comprende la produccion industrializacion y comercialización de productos agropecuarios forestales y otros recursos naturales biológicos."
          },
          
          "c4":{            
            "id": 4,
            "read": True,
            "status": 1,
            "order": 2,
            "name": "Finance",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-04.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },

          "c5":{            
            "id": 5,
            "read": True,
            "status": 1,
            "order": 5,
            "name": "Insurance",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-05.png",
            "description": "Lorem ipsum dolor sit amet, consetetur"

          },
          "c6":{            
            "id": 6,
            "read": True,
            "status": 1,
            "order": 14,
            "name": "Corporate Law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-10.png",
            "description": "Lorem ipsum dolor sit amet, consetetur"

          },
          "c7":{            
            "id": 7,
            "read": True,
            "status": 1,
            "order": 4,
            "name": "Foreign trade",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-06.png",
            "description": "Lorem ipsum dolor sit amet, consetetur"

          },
          "c8":{            
            "id": 8,
            "read": True,
            "status": 1,
            "order": 11,
            "name": "Information Technology",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-08.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c9":{            
            "id": 9,
            "read": True,
            "status": 1,
            "order": 13,
            "name": "Intellectual property",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-17-2.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c10":{            
            "id": 10,
            "read": True,
            "status": 1,
            "order": 7,
            "name": "Advertising",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-07.png",
            "description": "Lorem ipsum dolor sit amet, consetetur adipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c12":{            
            "id": 12,
            "read": True,
            "status": 1,
            "order": 12,
            "name": "Contracting with the State",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-24.png",
            "description": "Lorem ipsum dolor sit amet, consete sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c13":{            
            "id": 13,
            "read": True,
            "status": 1,
            "order": 8,
            "name": "Marketing",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-29-1.png",
            "description": "Lorem ipsum dolor sit amet, consetetut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          
          "c15":{            
            "id": 15,
            "read": True,
            "status": 1,
            "order": 15,
            "name": "Notary and Registry Law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-16.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunttuas"

          },
          "c16":{            
            "id": 16,
            "read": True,
            "status": 1,
            "order": 10,
            "name": "Project management",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-30-1.png",
            "description": "Lorem ipsum dolor sit amet, consetetur ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          

          "c18":{            
            "id": 18,
            "read": True,
            "status": 1,
            "order": 6,
            "name": "Civil Procedural Law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-12.png",
            "description": "Lorem ipsum dolor sit amet, consetetur ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c21":{            
            "id": 21,
            "read": True,
            "status": 1,
            "order": 3,
            "name": "Criminal law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-14.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunptuas"

          },
          "c24":{            
            "id": 24,
            "read": True,
            "status": 1,
            "order": 9,
            "name": "Labor Law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-11.png",
            "description": "Lorem ipsum dolor sit amet, consetetur ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },


          "c2":{            
            "id": 2,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Accounting",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-03.png",
            "description": "es la parte de la industria que se encarga de todos los procesos relacionados con la cadena alimentaria. "

          },
          "c3":{            
            "id": 3,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Tax Law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-17.png",
            "description": "uso de sistemas o elementos computarizadosy electromecánicos para controlar maquinarias o procesos industriales"

          },
          "c11":{            
            "id": 11,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "People Management",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Especialidades-09.png",
            "description": "Lorem ipsum dolor sit amet, consetetur ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },"c14":{            
            "id": 14,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Mechanics",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-24-1.png",
            "description": "Lorem ipsum dolor sit amet, conseteturidunt ptuas"

          },"c17":{            
            "id": 17,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Electricity",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-20-1.png",
            "description": "Lorem ipsum dolor sit amet, consetetur nt tuas"

          },"c19":{            
            "id": 19,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Agroindustry",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-21-3.png",
            "description": "Lorem ipsum dolor sit amet, conseteturnt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c20":{            
            "id": 20,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Electronics",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-22-1.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidutuas"

          },"c22":{            
            "id": 22,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Food",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-27.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c23":{            
            "id": 23,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Automation",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-23-2.png",
            "description": "Lorem ipsum dolor sit amet, conseteturnt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },"c25":{            
            "id": 25,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Gastronomy",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-28-2.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor inviduntut labore et dolore magna aliquyam erat, sed diam voluptuas"

          },
          "c26":{            
            "id": 26,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Plastics",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/06/Sin-título-1-26.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunttuas"

          },
          "c27":{            
            "id": 27,
            "read": True,
            "status": 2,
            "order": 0,
            "name": "Mining Law",
            "image": "http://www.linkup.com.pe/wp-content/uploads/2017/05/Sin-título-1-15.png",
            "description": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptuas"

          }
    }
