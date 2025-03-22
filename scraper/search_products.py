from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pinecone import Pinecone
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Init FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init Pinecone client (safe globally)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

@app.get("/search")
async def hybrid_search(request: Request):
    query = request.query_params.get("q", "")
    top_k = int(request.query_params.get("limit", 15))

    if not query:
        return {"error": "Query is missing"}

    try:
        # ✅ Lazy-load imports inside the route
        from sentence_transformers import SentenceTransformer
        from pinecone_text.sparse import BM25Encoder

        # ✅ Init lightweight model + encoder here
        model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
        sparse_encoder = BM25Encoder().default()

        dense = model.encode(query, normalize_embeddings=True).tolist()
        sparse = sparse_encoder.encode_documents([query])[0]

        results = index.query(
            vector=dense,
            sparse_vector=sparse,
            top_k=top_k,
            include_metadata=True
        )

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
@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"message": "🚀 Product Hunt Search API is running!"}
