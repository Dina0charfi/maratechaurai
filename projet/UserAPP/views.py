from email.mime import text
from multiprocessing import context
import os
import sys
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from .utils_sign import get_sign_for_word

from pathlib import Path
from .utils import arabic_to_latin  # si tu as ta fonction de translittération

REPO_ROOT = settings.BASE_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from speech_to_text_vosk_web import convert_to_wav, transcribe_file, wav_has_audio


def home(request):
    return render(request, "home.html")


def transcribe(request):
    context = {"text": "", "error": "", "translit": "", "sign_image": None}

    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        if not audio_file:
            context["error"] = "Aucun fichier audio reçu."
        elif audio_file.size == 0:
            context["error"] = "Fichier audio vide."
        else:
            upload_dir = settings.MEDIA_ROOT / "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            storage = FileSystemStorage(location=upload_dir)
            filename = storage.save(audio_file.name, audio_file)
            file_path = storage.path(filename)
            wav_path = None
            try:
                ext = Path(file_path).suffix.lower()
                if ext != ".wav":
                    wav_path = str(Path(file_path).with_suffix(".wav"))
                    convert_to_wav(file_path, wav_path)
                    if not wav_has_audio(wav_path):
                        raise RuntimeError("Audio trop court ou vide.")
                    text = transcribe_file(wav_path)
                else:
                    if not wav_has_audio(file_path):
                        raise RuntimeError("Audio trop court ou vide.")
                    text = transcribe_file(file_path)

                context["text"] = text

                # ---- NOUVEAU : translit arabe -> latin ----
                # Après avoir transcrit et translittéré
                translit_word = arabic_to_latin(text)
                sign_image = get_sign_for_word(translit_word)
                context["translit"] = translit_word
                context["sign_image"] = sign_image



                

            except Exception as exc:
                context["error"] = f"Transcription échouée : {exc}"
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if wav_path and os.path.exists(wav_path):
                    os.remove(wav_path)

    return render(request, "transcribe.html", context)
