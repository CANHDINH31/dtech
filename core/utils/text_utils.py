import re

def clean_text(text: str) -> str:
    # Bỏ ký tự xuống dòng, dấu *, dấu ** markdown
    text = re.sub(r'\n+', ' ', text)              # bỏ dòng mới
    text = re.sub(r'\*+', '', text)               # bỏ dấu * và **
    text = re.sub(r'\s+', ' ', text)              # chuẩn hóa khoảng trắng
    return text.strip()

def extract_keywords(question: str) -> list[str]:
    # Đưa về chữ thường
    text = question.lower().strip()

    # Danh sách các cụm từ dẫn cần loại bỏ
    patterns_to_remove = [
        r"khẳng định nào sau đây là (đúng|sai)",
        r"câu nào sau đây là (đúng|sai)",
        r"chọn (câu|đáp án) (đúng|sai)",
        r"(câu|khẳng định|nhận định) nào đúng",
        r"(câu|khẳng định|nhận định) nào sai",
        r"(đúng|sai) với nội dung.*?",
        r"về\s+",  # để tách keyword phía sau "về"
    ]

    # Loại bỏ các cụm từ dẫn
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text)

    # Loại bỏ dấu câu
    text = re.sub(r'[^\w\s]', '', text)

    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()

    # Trả về các từ khóa (nếu cần bạn có thể lọc thêm stopwords)
    keywords = text.split()
    return keywords


