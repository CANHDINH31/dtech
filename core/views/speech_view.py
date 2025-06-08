import os
from pydub import AudioSegment
from pydub.utils import which
import speech_recognition as sr
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
import uuid

# Khai báo đường dẫn ffmpeg nếu cần
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

class SpeechView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        print("FILES:", request.FILES)
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({'error': 'Không có file được upload'}, status=400)

        # Lưu file tạm
        unique_filename = f"{uuid.uuid4().hex}_{get_valid_filename(audio_file.name)}"
        temp_path = default_storage.save(unique_filename, audio_file)
        full_path = default_storage.path(temp_path)

        try:
            # Đọc file và chuyển sang wav nếu cần
            sound = AudioSegment.from_file(full_path)
            wav_path = full_path.rsplit(".", 1)[0] + ".wav"
            sound.export(wav_path, format="wav")

            # Nhận diện giọng nói
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language='vi-VN')
                except sr.UnknownValueError:
                    text = "Không nhận diện được âm thanh"

            # Xoá file wav tạm
            if os.path.exists(wav_path):
                os.remove(wav_path)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)

        return Response({"transcript": text})
