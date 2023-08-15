from sentence_transformers import SentenceTransformer


model = None


def embed(text):
    global model
    if not model:
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model.encode(text)
