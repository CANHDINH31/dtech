from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import numpy as np

# 1. Kho dữ liệu mẫu (giả sử bạn có nhiều tài liệu)
documents = [
    "Học máy là lĩnh vực trí tuệ nhân tạo liên quan đến việc xây dựng các mô hình tự học.",
    "Trí tuệ nhân tạo đang phát triển mạnh mẽ trong nhiều lĩnh vực khác nhau.",
    "Đạo văn là hành vi sao chép ý tưởng hoặc nội dung mà không trích dẫn nguồn.",
    "Máy học giúp máy tính nhận diện mẫu và dự đoán kết quả.",
    "Bài luận về trí tuệ nhân tạo và ứng dụng trong công nghiệp."
]

# 2. Tạo TF-IDF vector cho toàn bộ kho dữ liệu
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)  # shape (n_docs, n_features)

# FAISS yêu cầu vector float32 và ma trận dạng numpy
tfidf_matrix = tfidf_matrix.astype(np.float32).toarray()

# 3. Khởi tạo index FAISS
dimension = tfidf_matrix.shape[1]
index = faiss.IndexFlatIP(dimension)  # IP = Inner Product, tương tự cosine similarity nếu vector chuẩn hóa

# Chuẩn hóa vector TF-IDF để dùng cosine similarity bằng inner product
def normalize_vectors(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / (norms + 1e-10)

tfidf_matrix = normalize_vectors(tfidf_matrix)

# Thêm vector vào index
index.add(tfidf_matrix)

# 4. Hàm kiểm tra đạo văn với đoạn văn bản mới
def check_plagiarism(query_text, top_k=3):
    # Tạo vector TF-IDF của đoạn văn bản mới
    query_vec = vectorizer.transform([query_text]).astype(np.float32).toarray()
    query_vec = normalize_vectors(query_vec)

    # Tìm kiếm top_k văn bản gần nhất trong index
    distances, indices = index.search(query_vec, top_k)  # distances là similarity scores

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        results.append({
            "similarity": float(dist),
            "document": documents[idx]
        })
    return results

# 5. Thử nghiệm
query = "Đạo văn"
results = check_plagiarism(query)

print("Top kết quả kiểm tra đạo văn:")
for r in results:
    print(f"- Similarity: {r['similarity']:.4f}, Document: {r['document']}")