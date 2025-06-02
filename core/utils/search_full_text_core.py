from sklearn.feature_extraction.text import TfidfVectorizer
import faiss
import numpy as np
from ..models import ResearchDocument

class PlagiarismChecker:
    def __init__(self):
        self.documents_queryset = list(ResearchDocument.objects())
        self.documents = [doc.content for doc in self.documents_queryset]

        if not self.documents:
            raise ValueError("Không có tài liệu trong cơ sở dữ liệu.")

        # TF-IDF vector hóa
        self.vectorizer = TfidfVectorizer()
        tfidf_matrix = self.vectorizer.fit_transform(self.documents).astype(np.float32).toarray()

        # Chuẩn hóa vector
        self.index = self._build_faiss_index(tfidf_matrix)

    def _normalize_vectors(self, vectors):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / (norms + 1e-10)

    def _build_faiss_index(self, vectors):
        vectors = self._normalize_vectors(vectors)
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        return index

    def check(self, query_text, top_k=3):
        query_vec = self.vectorizer.transform([query_text]).astype(np.float32).toarray()
        query_vec = self._normalize_vectors(query_vec)
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            doc = self.documents_queryset[idx]
            results.append({
                "similarity": float(dist),
                "author": doc.author,
                "title": doc.title,
                "year": doc.year,
                "content": doc.content
            })
        return results
