from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from pinecone_text.sparse import BM25Encoder
from pinecone import Pinecone
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Init FastAPI app
app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Use lightweight transformer model
model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
sparse_encoder = BM25Encoder().default()

# Init Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

@app.get("/search")
async def hybrid_search(request: Request):
    query = request.query_params.get("q", "")
    top_k = int(request.query_params.get("limit", 15))

    if not query:
        return {"error": "Query is missing"}

    try:
        # Create dense + sparse embeddings
        dense = model.encode(query, normalize_embeddings=True).tolist()
        sparse = sparse_encoder.encode_documents([query])[0]

        # Query Pinecone
        results = index.query(
            vector=dense,
            sparse_vector=sparse,
            top_k=top_k,
            include_metadata=True
        )

        # Format response
        formatted_results = []
        for i, match in enumerate(results["matches"], 1):
            meta = match.get("metadata", {})

            formatted_results.append({
                "rank": i,
                "name": meta.get("name", "Unknown"),
                "tagline": meta.get("tagline") or meta.get("header", "No tagline"),
                "description": meta.get("description", "")[:400],
                "tags": meta.get("tags", []),
                "logo_url": meta.get("logo_url") or "https://via.placeholder.com/100",
                "url": meta.get("url") or "#",
                "score": round(match.get("score", 0), 4)
            })

        return {"products": formatted_results}

    except Exception as e:
        return {"error": str(e)}
