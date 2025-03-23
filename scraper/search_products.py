import streamlit as st
from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder
from pinecone import Pinecone
from dotenv import load_dotenv
import os
import nltk

# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize model and Pinecone
model = SentenceTransformer("paraphrase-MiniLM-L3-v2")  # lightweight
sparse_encoder = BM25Encoder().default()

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# --- Streamlit UI ---
st.set_page_config(page_title="Product Hunt Search", layout="centered")

# Optional styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .stImage > img {
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# App title
st.title("🔍 Product Hunt Hybrid Search")

# Query input
query = st.text_input("Enter your product idea or query:")

if query:
    with st.spinner("🔎 Searching..."):
        # Create dense and sparse vectors
        dense = model.encode(query, normalize_embeddings=True).tolist()
        sparse = sparse_encoder.encode_documents([query])[0]

        # Query Pinecone
        results = index.query(
            vector=dense,
            sparse_vector=sparse,
            top_k=15,
            include_metadata=True
        )

        st.subheader(f"✨ Results for: '{query}'")

        for i, match in enumerate(results["matches"], 1):
            meta = match["metadata"]
            with st.container():
                cols = st.columns([1, 4])

                with cols[0]:
                    st.image(
                        meta.get("logo_url") or "https://via.placeholder.com/100",
                        width=80
                    )

                with cols[1]:
                    st.markdown(f"### {meta.get('name', 'Unknown')}")
                    st.markdown(f"**{meta.get('tagline') or meta.get('header', '')}**")
                    st.write(meta.get("description", "")[:300])
                    st.markdown(f"**Tags**: `{', '.join(meta.get('tags', []))}`")
                    st.markdown(f"[🔗 Visit Product]({meta.get('url', '#')})")
                    st.markdown(f"**Score**: `{round(match.get('score', 0), 4)}`")

                st.divider()
