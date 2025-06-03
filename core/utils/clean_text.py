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
