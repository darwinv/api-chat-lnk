"""
    Archivo creado con la finalidad de crear funciones y clases que permitan trabajar de forma estandar
    el manejo de variables, ejemplo: capitalizar el primer caracter
"""
def capitalize(line):
    """
        Funcion creada como erramienta para capitalizar el primer caracter de una cadena
        sin modificar el resto de la cadena
    """

    if len(line) <= 0:
        return ''
    return line[0].upper() + line[1:]