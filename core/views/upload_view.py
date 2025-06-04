from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from docx import Document as DocxDocument
from docx.enum.text import WD_COLOR_INDEX
import re

class UploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Chưa chọn file"}, status=status.HTTP_400_BAD_REQUEST)

        if not file.name.endswith('.docx'):
            return Response({"error": "Chỉ hỗ trợ file .docx"}, status=status.HTTP_400_BAD_REQUEST)

        # Lưu tạm file
        filepath = f"/tmp/{file.name}"
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            questions = self.extract_questions_with_answers(filepath)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "filename": file.name,
            "total_questions": len(questions),
            "questions": questions
        })

    def extract_questions_with_answers(self, file_path):
        doc = DocxDocument(file_path)
        paragraphs = [p for p in doc.paragraphs if p.text.strip()]
        
        questions = []
        i = 0
        while i < len(paragraphs):
            para_text = paragraphs[i].text.strip()

            # Nếu dòng hiện tại là "Câu x:"
            if re.match(r"^Câu\s*\d+[:：]?", para_text):
                question_text = para_text

                # Nếu dòng kế tiếp là nội dung câu hỏi (không phải đáp án), gộp vào
                if i + 1 < len(paragraphs) and not re.match(r"^[A-Da-d][\.\)]", paragraphs[i + 1].text.strip()):
                    question_text += " " + paragraphs[i + 1].text.strip()
                    i += 1

                # Tiếp theo là 4 đáp án
                answers = []
                for j in range(1, 5):
                    if i + j >= len(paragraphs):
                        break
                    answer_para = paragraphs[i + j]
                    text = answer_para.text.strip()
                    is_correct = any(
                        run.font.highlight_color == WD_COLOR_INDEX.YELLOW
                        for run in answer_para.runs
                    )
                    answers.append({
                        "text": text,
                        "is_correct": is_correct
                    })

                questions.append({
                    "question": question_text,
                    "answers": answers
                })

                i += 5  # Nhảy tới câu tiếp theo
            else:
                i += 1

        return questions