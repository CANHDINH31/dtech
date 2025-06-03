import re

def clean_text(text: str) -> str:
    # Loại bỏ khoảng trắng đầu cuối
    text = text.strip()
    # Chuyển về chữ thường
    text = text.lower()
    # Loại bỏ ký tự đặc biệt, chỉ giữ chữ, số, dấu cách
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Loại bỏ nhiều khoảng trắng thành 1 khoảng trắng
    text = re.sub(r'\s+', ' ', text)
    return text

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


