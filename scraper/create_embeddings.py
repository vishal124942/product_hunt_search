import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTS_PATH = Path("products_data.json")
EMBED_MODEL = "all-MiniLM-L6-v2"
DIMENSIONS = 384
PINECONE_INDEX_NAME = "ph-products-index"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

def create_text(company):
    tag_text = " | ".join(company.get("tags", []))
    return f"""{company.get('name', '')}
{company.get('tagline', '')}
{company.get('description', '')}
{tag_text}"""

def main():
    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)
    # Filter out companies with null name, tagline, or description
    clean_companies = [
        c for c in companies if c.get("name") and c.get("tagline") and c.get("description")
    ]
    print(f"📦 Found {len(clean_companies)} clean companies")
    # Initialize dense embedding model
    model = SentenceTransformer(EMBED_MODEL)
    # Initialize sparse encoder
    bm25_encoder = BM25Encoder().default()
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=DIMENSIONS,
        # Required for Hybrid Search
        metric="dotproduct",  
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(PINECONE_INDEX_NAME)
    vectors = []
    for i, company in enumerate(clean_companies, 1):
        text = create_text(company)
        dense_vec = model.encode(text, normalize_embeddings=True).tolist()
        sparse_vec = bm25_encoder.encode_documents([text])[0]
        vectors.append({
            "id": f"product-clean-{i}",
            "values": dense_vec,
            "sparse_values": sparse_vec,
            "metadata": {
                "name": company.get("name"),
                "tagline": company.get("tagline"),
                "description": company.get("description"),
                "tags": company.get("tags"),
                "logo_url": company.get("logo_url"),
                "url": company.get("url"),
                "full_text": text
            }
        })

    print(f"Uploading {len(vectors)} clean vectors...")
    index.upsert(vectors=vectors)
    print(" Upload complete.")

if __name__ == "__main__":
    main()
