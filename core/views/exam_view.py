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
                
                # Tìm dòng bắt đầu bằng "Câu" + số
                question_match = re.match(r'^Câu\s*\d+([a-zA-Z]*)\s*[:.]?\s*$', line, re.IGNORECASE)
                if question_match:
                    question_text = ""
                    
                    # Lấy phần còn lại của dòng sau "Câu X:"
                    remaining_line = re.sub(r'^Câu\s*\d+[:\s]*', '', line, flags=re.IGNORECASE).strip()
                    if remaining_line:
                        question_text = remaining_line
                    
                    i += 1
                    
                    # Đọc các dòng tiếp theo cho đến khi gặp đáp án hoặc câu mới
                    while i < len(lines):
                        current_line = lines[i].strip()
                        
                        # Dừng nếu gặp đáp án (các pattern khác nhau)
                        if self._is_answer_line(current_line):
                            break
                        
                        # Dừng nếu gặp câu hỏi mới
                        if re.match(r'^Câu\s*\d+', current_line, re.IGNORECASE):
                            i -= 1  # Lùi lại để xử lý câu này
                            break
                        
                        # Bỏ qua các dòng nhiễu
                        if not self._is_noise_line(current_line):
                            if question_text:
                                question_text += " " + current_line
                            else:
                                question_text = current_line
                        
                        i += 1
                    
                    # Làm sạch và lưu câu hỏi
                    if question_text:
                        cleaned_question = self._clean_question_text(question_text)
                        
                        if cleaned_question and len(cleaned_question) >= 10:
                            questions.append({"question_text": cleaned_question})
                else:
                    i += 1
        
        # Loại bỏ trùng lặp
        return self._remove_duplicates(questions)

    def _is_answer_line(self, line):
        """Kiểm tra xem dòng có phải là đáp án không"""
        answer_patterns = [
            r'^[ABCD]\.', # A. B. C. D.
            r'^Ó\s*[ABCD]', # Ó A, Ó B
            r'^[○●]\s*[ABCD]', # ○ A, ● B  
            r'^[ABCD]\s+[A-ZÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶ]', # A Luôn xác định...
            r'^ọ\s*[ABCD]', # ọ A, ọ B
            r'^Đi\s*[ABCD]' # Đi B
        ]
        
        for pattern in answer_patterns:
            if re.match(pattern, line):
                return True
        return False

    def _is_noise_line(self, line):
        """Kiểm tra xem dòng có phải là nhiễu không"""
        if not line or len(line.strip()) == 0:
            return True
        
        noise_patterns = [
            r'^Gần cờ\s*$',
            r'^Thoát\s*$', 
            r'^Luyện tập trắc nghiệm',
            r'^Luật dân sự\s*\d*\s*$',
            r'^[^\w\sÀ-ỹ]+$', # Chỉ chứa ký tự đặc biệt
            r'^\d+\s*$', # Chỉ có số
            r'^[a-zA-Z]{1,3}\s+[0-9]+\s*[a-zA-Z]*\s*$', # Các code lạ
            r'^[hb]\s*$' # Các ký tự đơn lẻ
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False

    def _clean_question_text(self, text):
        """Làm sạch văn bản câu hỏi"""
        # Loại bỏ đáp án nếu có lẫn vào
        text = self._remove_embedded_answers(text)
        
         # Loại bỏ phần sau dấu ":" nếu có
        text = re.sub(r':.*$', '', text)
        
        # Chuẩn hóa khoảng trắng
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Loại bỏ các cụm từ nhiễu
        noise_phrases = [
            r'Gần cờ',
            r'Thoát', 
            r'Luyện tập trắc nghiệm Chương \d+',
            r'Luật dân sự \d*',
            r'\b[a-zA-Z]{1,2}\s+\d+\s+[a-zA-Z]*\b', # Code lạ
            r'\bSá b\b',
            r'\bR b\b',
            r'\bAn \d+ b\b'
        ]
        
        for pattern in noise_phrases:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Loại bỏ ký tự lạ ở đầu và cuối
        text = re.sub(r'^[^\w\sÀ-ỹ]+|[^\w\sÀ-ỹ?:.!]+$', '', text)
        
        # Chuẩn hóa lại khoảng trắng sau khi xử lý
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text

    def _remove_embedded_answers(self, text):
        """Loại bỏ đáp án có thể lẫn vào câu hỏi"""
        # Pattern để tìm và loại bỏ đáp án
        answer_patterns = [
            r'\s+[ABCD]\.?\s+[A-ZÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶ][^.?:]*',
            r'\s+Ó\s*[ABCD]\.?\s+[^.?:]*',
            r'\s+ọ\s*[ABCD]\.?\s+[^.?:]*',
            r'\s+Đi\s*[ABCD]\.?\s+[^.?:]*'
        ]
        
        for pattern in answer_patterns:
            # Tìm vị trí đầu tiên của đáp án và cắt phần trước đó
            match = re.search(pattern, text)
            if match:
                text = text[:match.start()]
                break
        
        return text.strip()

    def _remove_duplicates(self, questions):
        """Loại bỏ câu hỏi trùng lặp"""
        unique_questions = []
        seen_texts = set()
        
        for q in questions:
            question_text = q["question_text"].lower().strip()
            # So sánh 50 ký tự đầu để tránh trùng lặp gần giống
            key = question_text[:50] if len(question_text) > 50 else question_text
            
            if key not in seen_texts:
                unique_questions.append(q)
                seen_texts.add(key)
        
        return unique_questions
