import os
import tempfile
from django.core.exceptions import ValidationError
from moviepy import VideoFileClip

def duracion_video(value):
    # Crear archivo temporal
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(value.name)[1]) as tmp:
            for chunk in value.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        clip = VideoFileClip(tmp_path)
        duracion_segundos = clip.duration
        clip.close()

        if duracion_segundos > 1200: 
            raise ValidationError("El video no puede durar más de 20 minutos.")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)