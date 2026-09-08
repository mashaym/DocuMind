import html

import streamlit as st
from rag_core import load_pipeline, answer_question

APP_NAME = "DocuMind"
APP_ICON = "🔍"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling — one accent color, used consistently throughout
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --accent: #0d9488;
        --accent-dark: #0f766e;
        --accent-light: #ccfbf1;
        --accent-tint: #f0fdfa;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 760px;
    }

    /* Header */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        margin-bottom: 1.1rem;
        background-color: var(--accent);
    }
    .app-header .icon { font-size: 2.4rem; line-height: 1; }
    .app-header .title { color: #ffffff; font-size: 1.7rem; font-weight: 700; margin: 0; }
    .app-header .subtitle { color: var(--accent-light); font-size: 0.95rem; margin-top: 0.15rem; }

    /* "What is this?" intro card */
    .intro-card {
        background-color: var(--accent-tint);
        border: 1px solid var(--accent-light);
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 1.4rem;
        color: #134e4a;
        font-size: 0.95rem;
        line-height: 1.55;
    }
    .intro-card .intro-title {
        font-weight: 700;
        color: var(--accent-dark);
        margin-bottom: 0.35rem;
        font-size: 1rem;
    }

    /* Example question chips */
    .examples-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin: 0.2rem 0 0.2rem 0;
    }
    .examples-caption {
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 0.6rem;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button {
        border-radius: 999px;
        border: 1px solid var(--accent-light);
        background-color: var(--accent-tint);
        color: var(--accent-dark);
        font-size: 0.85rem;
        padding: 0.35rem 0.9rem;
        white-space: normal;
        height: auto;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        border-color: var(--accent);
        background-color: var(--accent-light);
        color: var(--accent-dark);
    }

    /* Ask button */
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 10px;
        background-color: var(--accent);
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.55rem 1.4rem;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: var(--accent-dark);
        color: white;
    }

    /* Answer card */
    .answer-card {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-left: 4px solid var(--accent);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
        line-height: 1.55;
        color: #111827;
    }
    .answer-card .answer-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--accent-dark);
        margin-bottom: 0.5rem;
    }

    /* Source pills */
    .pill-row { margin-top: 0.8rem; display: flex; flex-wrap: wrap; gap: 0.4rem; }
    .pill {
        display: inline-block;
        background-color: var(--accent-tint);
        color: var(--accent-dark);
        border: 1px solid var(--accent-light);
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        font-size: 0.78rem;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Engine (loaded once, per the required interface)
# --------------------------------------------------------------------------
@st.cache_resource
def get_pipeline():
    return load_pipeline()


embedder, collection = get_pipeline()

DOCUMENTS = [
    ("🚴 Summit Cycles", "a fictional bicycle company handbook"),
    ("☕ Ember Coffee", "a fictional coffee roaster handbook"),
    ("🫖 Brightwave Kettles", "a fictional kettle company handbook"),
]

EXAMPLE_QUESTIONS = [
    "How much does the Aquila cost?",
    "What is the company mascot?",
    "What coffee blends does Ember sell?",
]

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### {APP_ICON} {APP_NAME}")
    st.write(
        "This app answers questions using only what's written in a set of "
        "documents — it never makes things up. Every answer tells you which "
        "document it came from."
    )

    st.markdown("### 📄 Sample documents")
    st.caption("Three made-up company handbooks, included just so you can try the app.")
    for name, desc in DOCUMENTS:
        st.markdown(
            f"**{name}**  \n<span style='color:#6b7280;font-size:0.85rem;'>{desc}</span>",
            unsafe_allow_html=True,
        )

    st.markdown("### ⚙️ How it works")
    st.write(
        "1. You ask a question in plain English.\n"
        "2. The app finds the most relevant bits of the documents.\n"
        "3. It writes an answer using only those bits, and shows you the source."
    )

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="app-header">
        <div class="icon">{APP_ICON}</div>
        <div>
            <div class="title">{APP_NAME}</div>
            <div class="subtitle">Ask a question in plain English — get an answer straight from your documents.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# "What is this?" intro
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="intro-card">
        <div class="intro-title">What is this?</div>
        {APP_NAME} lets you ask questions about a set of documents in everyday words,
        instead of reading through them yourself. Type your question below, and it
        will search the documents, write you an answer based only on what they say,
        and show you exactly which document that answer came from.
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "question_box" not in st.session_state:
    st.session_state.question_box = ""
if "run_query" not in st.session_state:
    st.session_state.run_query = False
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
    st.session_state.last_sources = None
    st.session_state.last_error = None

# --------------------------------------------------------------------------
# Example questions
# --------------------------------------------------------------------------
st.markdown('<div class="examples-label">Try an example (using our sample documents):</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="examples-caption">These use the fictional handbooks above — you don\'t need to know '
    'anything about them, just tap one and see how it works.</div>',
    unsafe_allow_html=True,
)
cols = st.columns(len(EXAMPLE_QUESTIONS))
for col, example in zip(cols, EXAMPLE_QUESTIONS):
    if col.button(example, use_container_width=True, key=f"example_{example}"):
        st.session_state.question_box = example
        st.session_state.run_query = True

# --------------------------------------------------------------------------
# Question input
# --------------------------------------------------------------------------
with st.form("qa_form"):
    st.text_input(
        "Your question",
        key="question_box",
        placeholder="e.g. How much does the Aquila cost?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Ask ➤", use_container_width=True)

if submitted:
    st.session_state.run_query = True

# --------------------------------------------------------------------------
# Run the query
# --------------------------------------------------------------------------
if st.session_state.run_query:
    st.session_state.run_query = False
    question = st.session_state.question_box.strip()
    if question:
        with st.spinner("Thinking..."):
            try:
                answer, retrieved_files = answer_question(embedder, collection, question)
                st.session_state.last_answer = answer
                st.session_state.last_sources = retrieved_files
                st.session_state.last_error = None
            except Exception as e:
                st.session_state.last_answer = None
                st.session_state.last_sources = None
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    st.session_state.last_error = (
                        "warning",
                        "Rate limit reached — please wait a bit and try again.",
                    )
                else:
                    st.session_state.last_error = ("error", f"Something went wrong: {e}")

# --------------------------------------------------------------------------
# Display results
# --------------------------------------------------------------------------
if st.session_state.last_error:
    kind, message = st.session_state.last_error
    if kind == "warning":
        st.warning(message)
    else:
        st.error(message)

if st.session_state.last_answer:
    answer_html = html.escape(st.session_state.last_answer).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-label">Answer</div>
            {answer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.last_sources:
        pills = "".join(
            f'<span class="pill">📄 {html.escape(src)}</span>'
            for src in st.session_state.last_sources
        )
        st.markdown(f'<div class="pill-row">{pills}</div>', unsafe_allow_html=True)
