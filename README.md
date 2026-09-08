# 🔍 DocuMind

DocuMind is a small Retrieval-Augmented Generation (RAG) app: you ask a
question in plain English, it searches a set of PDF documents for the most
relevant passages, and it asks an LLM (Google Gemini) to write an answer
**using only those passages** — then shows you exactly which document the
answer came from. It's a Streamlit web app backed by a local vector database
(ChromaDB) and sentence-embedding search (Sentence-Transformers).

Nothing is invented outside the documents: if the answer isn't in the source
material, the app is instructed to say so instead of guessing.

## What's in this repo

The app ships with three **fictional, made-up company handbooks** used purely
as demo content:

| File | Company | About |
|---|---|---|
| `docs/summit_cycles.pdf` | Summit Cycles | a fictional bicycle company |
| `docs/ember_coffee.pdf` | Ember Coffee | a fictional coffee roaster |
| `docs/brightwave_kettles.pdf` | Brightwave Kettles | a fictional kettle company |

You can ask things like *"How much does the Aquila cost?"* or *"What is the
company mascot?"* — try the example buttons on the app's home screen.

To point DocuMind at your own documents, just drop your PDFs into `docs/`
(see [Adding your own documents](#adding-your-own-documents) below).

## How it works

1. **Ingest (first run only).** Every PDF in `docs/` is read page-by-page,
   the text is cleaned up, and split into overlapping ~500-character,
   sentence-aware chunks (`rag_core.chunk_text`).
2. **Embed & store.** Each chunk is turned into a vector with the
   `all-MiniLM-L6-v2` Sentence-Transformers model and saved, along with which
   file it came from, into a persistent [ChromaDB](https://www.trychroma.com/)
   collection on disk (`chroma_db/`). This only happens once — on later runs
   the existing database is reused.
3. **Retrieve.** When you ask a question, it's embedded with the same model
   and used to look up the 3 most similar chunks in the database, across all
   documents.
4. **Augment.** Those chunks are assembled into a prompt that labels each
   chunk with its source file and instructs the model to answer *only* from
   that context, and to say "I could not find that in the documents" if the
   answer isn't there.
5. **Generate.** The prompt is sent to Google's `gemini-3.5-flash-lite`
   model, which returns the answer. The app displays the answer alongside
   pills showing which file(s) the retrieved chunks came from.

This pipeline (steps 1–5) lives entirely in `rag_core.py`. The Streamlit UI
in `app.py` is just a presentation layer on top of it.

## Project structure

```
rag-project/
├── app.py              # Streamlit UI — the app you actually run
├── rag_core.py          # RAG engine: ingest, embed, retrieve, generate
├── evaluate.py           # Small regression test suite for the engine
├── docs/                 # Sample PDF documents (fictional handbooks)
├── requirements.txt       # Pinned Python dependencies
├── .env.example           # Template for your .env (copy and fill in)
└── .gitignore
```

`chroma_db/` (the built vector database) and `venv/` are not committed — both
are generated locally (see Setup below).

## Setup

**Requirements:** Python 3.10+ and a
[Gemini API key](https://aistudio.google.com/apikey).

```bash
# 1. Clone and enter the project
git clone <this-repo-url>
cd rag-project

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
# then edit .env and paste your key in place of the placeholder

# 5. Run the app
streamlit run app.py
```

On the very first run, DocuMind will read the PDFs in `docs/`, embed them,
and build `chroma_db/` on disk — this can take a little while. Every run
after that loads the existing database instantly.

## Adding your own documents

Drop additional (or replacement) PDF files into `docs/`, delete the
`chroma_db/` folder so it gets rebuilt from scratch, and restart the app.

## Evaluating answer quality

`evaluate.py` runs a fixed set of questions with known expected keywords
against the engine and reports a pass/fail score — a quick regression check
after changing the chunking, retrieval, or prompt logic in `rag_core.py`:

```bash
python evaluate.py
```

## Error handling

If the Gemini API is rate-limited (`RESOURCE_EXHAUSTED` / HTTP 429), the app
shows a friendly "please wait and try again" warning instead of crashing;
any other failure shows a generic error message with the underlying
exception text.

## Tech stack

- **UI:** [Streamlit](https://streamlit.io/)
- **Embeddings:** [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
- **Vector store:** [ChromaDB](https://www.trychroma.com/) (persistent, local, on-disk)
- **PDF parsing:** [pypdf](https://pypdf.readthedocs.io/)
- **LLM:** [Google Gemini](https://ai.google.dev/) via the `google-genai` SDK
