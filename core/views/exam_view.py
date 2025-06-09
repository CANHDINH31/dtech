import os
import cv2
import pytesseract
import tempfile
import re

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status


class ExamView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Chưa chọn file"}, status=status.HTTP_400_BAD_REQUEST)

        # Bước 1: Lưu video tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            for chunk in file.chunks():
                temp_video.write(chunk)
            video_path = temp_video.name

        try:
            text_blocks = self.extract_text_from_video(video_path)
            questions = self.extract_questions(text_blocks)
            
            unique_questions = list(set(q["question_text"] for q in questions))

            return Response({
                "text_blocks": text_blocks,
                "questions": unique_questions,
                "length": len(unique_questions)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

    def extract_text_from_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * 1.5) if fps > 0 else 30
        count = 0
        text_blocks = []

        custom_config = r'--oem 3 --psm 6'
        last_text = ""

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if count % frame_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                text = pytesseract.image_to_string(thresh, lang='vie', config=custom_config)

                cleaned = self.clean_ocr_text(text)
                if cleaned and cleaned != last_text:
                    text_blocks.append(cleaned)
                    last_text = cleaned
            count += 1
        cap.release()
        return text_blocks

    def clean_ocr_text(self, text):
        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            noise_patterns = [
                r'.*ChatGPT.*', r'.*tmu\.edu.*', r'.*RFS-ADRENO.*',
                r'.*courses.*test.*', r'.*Nộp bài.*', r'.*Theo dõi.*',
                r'.*Gắn cờ.*', r'.*dấu trang.*', r'.*bookmark.*',
                r'.*NhữngGIAnhNói.*', r'.*CreateNetApp.*', r'.*Panckev.*',
                r'.*245920.*', r'^[0-9\s\.\-]+$', r'.*[xX].*[xX].*[xX].*',
                r'.*w\s+rẻ\s+0.*', r'.*3P\..*',
            ]
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in noise_patterns):
                continue

            line = re.sub(r'[^\w\s,.?:()ÁÀẠẢÃĂÂÊÔƠƯĐđàáảãạăâếềễệểờởỡợứừữựữĩỉịịỳýỷỹỵ\-.]', ' ', line)
            line = re.sub(r'\s+', ' ', line).strip()

            if len(line) < 3:
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)
    
    def extract_questions(self, text_blocks):
        questions = []

        for block in text_blocks:
            lines = block.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if re.match(r'^Câu\s*\d+', line, re.IGNORECASE):
                    question_text = ""
                    i += 1

                    # while i < len(lines):
                    #     current_line = lines[i].strip()

                    #     # Nếu dòng bắt đầu bằng đáp án A/B/C/D => kết thúc câu hỏi
                    #     if re.match(r'^[ABCD]\s', current_line):
                    #         break

                    #     question_text += " " + current_line
                    #     i += 1

                    question_text = question_text.strip()

                    # Nếu câu hỏi vẫn còn kèm dấu ? hoặc : thì có thể cắt tại đó
                    match = re.search(r'(.+?[?:])', question_text)
                    if match:
                        question_text = match.group(1).strip()

                    questions.append({"question_text": question_text})
                else:
                    i += 1

        return questions
