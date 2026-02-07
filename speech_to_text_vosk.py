import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import sys
sys.stdout.reconfigure(encoding='utf-8')

# تحميل الموديل
model = Model(r"C:\vosk-model-ar")

samplerate = 16000
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

print(" تكلّم توّا... (Ctrl+C للإيقاف)")

with sd.RawInputStream(
    samplerate=samplerate,
    blocksize=8000,
    dtype='int16',
    channels=1,
    callback=callback
):
    rec = KaldiRecognizer(model, samplerate)
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print("📝:", result.get("text", ""))
