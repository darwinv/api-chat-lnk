"""
    Archivo creado con la finalidad de crear funciones y clases que permitan
    trabajar de forma estandar
    el manejo de variables, ejemplo: capitalizar el primer caracter
"""
import datetime, string, random, boto3, os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from datetime import datetime as date_time, date, time, timedelta
from moviepy.editor import *
from PIL import Image
from api.logger import manager
logger = manager.setup_log(__name__)

def capitalize(line):
    """
        Funcion creada como herramienta para capitalizar el primer caracter de una cadena
        sin modificar el resto de la cadena
    """

    if len(line) <= 0:
        return ''
    return line[0].upper() + line[1:]

def get_date_by_time(validity_months):
    """
    funcion creada para calcular la fecha, segun cantidad en meses dada
    ( 1 mes son 30 dias)
    :param validity_months: Numero entero en meses
    :return: datetime.date
    """
    return datetime.date.today() + datetime.timedelta(validity_months*365/12)

def get_time_message(date_time_message):
    """
    funcion devuelve el tiempo en string de una fecha pasada
    :param date_time_message: Numero entero en meses
    :return: string?
    """
    try:
        date_message = date_time_message.date()
        date_time_message = date_time_message
        if date_message == date.today():
            # tiempo = time(date_time_message.hour, date_time_message.minute)
            return date_time_message
        elif date_message == date.today() - timedelta(days=1):
            return str(_('yesterday'))
        else:
            return date_time.strftime(date_message, '%d/%m/%y')
    except Exception as e:
        pass
    return None


def ramdon_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def s3_upload_file(file, filename):
    """Subir archivo usando put object."""
    client = boto3.client('s3')
    client.put_object(
        ACL='public-read',
        ContentType=file.content_type,
        Bucket='linkup-photos',
        Body=file.read(),  # 'bytes or seekable file-like object',
        Key=filename
    )
    # file.close()
    return 'https://s3.amazonaws.com/linkup-photos/' + filename


def resize_img(file, size):
    """
        file type image
        size int of image thumb
    """
    # media_type = file.content_type.split("/")[0]
    # import pdb
    # pdb.set_trace()

    extension = file.name.split(".")[-1]

    if extension == 'png' or extension == 'jpg' or extension == 'gif':
        pass
    elif extension == 'mp4':
        return thumb_video(file, size)
    else:
        return None

    image = Image.open(file)

    width, height = image.size

    if width > height:
        factor = size / width
    else:
        factor = size / height

    thumb = image.resize((int(width * factor), int(height * factor)))

    thumb.save(file.name,image.format, quality=95)

    data = open(file.name,'rb')

    data.content_type = file.content_type

    return data


def thumb_video(file, size):
    # from shutil import copyfile
    # file_content = file.read()
    path = default_storage.save('tmp/{}'.format(file.name), ContentFile(file.read()))
    print(path)
    clip = VideoFileClip(path)
    import pdb; pdb.set_trace()
    thumb = os.path.join("api/", "th_%s.jpg" % file.name)
    clip.save_frame(thumb, t=random.uniform(0.1, clip.duration))
    dst = 'api/th_{}'.format(file.name)
    # copyfile(src, dst)
    data = open(dst, 'rb')
    data.content_type = 'image/jpg'
    # default_storage.delete(path)
    return data

def remove_file(file):
    """Remove File from Disk"""
    if file:
        file.close()
        if os.path.exists(file.name):
            try:
                os.remove(file.name)
            except Exception as e:
                print(e.strerror)
                logger.warning(e.strerror)

def clear_data_no_valid(data,valid_fields):
    """
    data: dict
    data: tuple for valid fields
    """
    # Eliminar data no valida
    data_auxiliar = dict(data)
    for field in data_auxiliar:
        if not field in valid_fields:
            data.pop(field, None)
