from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from docx import Document as DocxDocument
from docx.enum.text import WD_COLOR_INDEX
import re
from ..models import Question
from mongoengine.errors import ValidationError

class UploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        print(file.name,"file")
        if not file:
            return Response({"error": "Chưa chọn file"}, status=status.HTTP_400_BAD_REQUEST)
        # Lưu tạm file
        filepath = f"/tmp/{file.name}"
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            questions = self.extract_questions_with_answers(filepath)
            saved_count = 0
            skipped_count = 0
            for q in questions:
                try:
                    q["question"] = self.remove_prefix(q["question"])  
                    if Question.objects.filter(question__iexact=q["question"]).first():
                        skipped_count += 1
                        continue
                    question_obj = self.convert_question(q)
                    question_obj.save()
                    saved_count += 1
                except (ValidationError, ValueError) as qe:
                    print(f"❌ Lỗi lưu câu hỏi: {qe}")
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "filename": file.name,
            "total_questions": len(questions),
            "saved_to_db": saved_count,
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
    
    
    def convert_question(self, raw_question):
        choices = ["a", "b", "c", "d"]
        answers = raw_question["answers"]
        
        if len(answers) != 4:
            raise ValueError(f"Không đủ 4 đáp án cho câu: {raw_question['question']}")
        
        correct_idx = next((i for i, ans in enumerate(answers) if ans["is_correct"]), None)
        if correct_idx is None:
            raise ValueError(f"Không tìm thấy đáp án đúng cho câu: {raw_question['question']}")
        
        return Question(
            question=raw_question["question"],
            a=answers[0]["text"],
            b=answers[1]["text"],
            c=answers[2]["text"],
            d=answers[3]["text"],
            correct_answer=choices[correct_idx]
        )
        
    def remove_prefix(self, question_text):
        # Loại bỏ tiền tố kiểu "Câu 1:", "Câu 18:",...
        return re.sub(r'^Câu\s*\d+:\s*', '', question_text).strip()