# rag_core.py — the shared "engine" for our RAG system
import warnings
warnings.filterwarnings("ignore")

import os
import re
import glob
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from google import genai

# Connect to Gemini once
load_dotenv()
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.5-flash-lite"


def chunk_text(text, chunk_size=500, overlap_sentences=1):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current, current_len = [], [], 0
    for sentence in sentences:
        if current_len + len(sentence) > chunk_size and current:
            chunks.append(" ".join(current))
            current = current[-overlap_sentences:]
            current_len = sum(len(s) for s in current)
        current.append(sentence)
        current_len += len(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


def load_all_documents(folder="docs"):
    all_chunks, all_metadatas = [], []
    pdf_paths = glob.glob(os.path.join(folder, "*.pdf"))
    for path in pdf_paths:
        filename = os.path.basename(path)
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append(chunk)
            all_metadatas.append({"source": filename, "chunk_number": i})
    return all_chunks, all_metadatas, pdf_paths


def load_pipeline():
    """Load the embedding model and the persistent database, building it once if empty."""
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection("documents")
    if collection.count() == 0:
        chunks, metadatas, pdf_paths = load_all_documents("docs")
        embeddings = embedder.encode(chunks)
        collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=[f"chunk_{i}" for i in range(len(chunks))],
        )
    return embedder, collection


def answer_question(embedder, collection, question, n_results=3):
    """Retrieve relevant chunks, build a grounded prompt, and return (answer, retrieved_files)."""
    question_embedding = embedder.encode(question)
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=n_results,
    )
    retrieved_chunks = results["documents"][0]
    retrieved_metas = results["metadatas"][0]

    context = "\n\n".join(
        f"[Source: {meta['source']}]\n{chunk}"
        for chunk, meta in zip(retrieved_chunks, retrieved_metas)
    )
    prompt = f"""Answer the question using ONLY the context below.
Each piece of context begins with its source file in square brackets.
If the answer is not in the context, say "I could not find that in the documents."
At the end of your answer, add a line starting with "Source:" naming the file(s) you used.

Context:
{context}

Question: {question}"""

    response = gemini.models.generate_content(model=MODEL_NAME, contents=prompt)
    retrieved_files = sorted(set(meta["source"] for meta in retrieved_metas))
    return response.text, retrieved_files