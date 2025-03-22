import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv
load_dotenv()
PRODUCTS_PATH = Path("products_data.json")
PINECONE_INDEX_NAME = "ph-products-index"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") 
EMBED_MODEL = "all-MiniLM-L6-v2"
DIMENSIONS = 384
def create_text(company):
    tag_text = " | ".join(company.get("tags", []))
    return f"""{company.get('name', '')}
{company.get('tagline', '')}
{company.get('description', '')}
{tag_text}"""

def main():
    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    null_companies = [
        c for c in companies
        if not c.get("name") or not c.get("tagline") or not c.get("description")
    ]
    print(f"Found {len(null_companies)} entries with nulls")
    model = SentenceTransformer(EMBED_MODEL)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    vectors = []
    for i, company in enumerate(null_companies, 1):
        text = create_text(company)
        embedding = model.encode(text, normalize_embeddings=True)

        vectors.append({
         "id": f"product-null-{i}",
         "values": embedding.tolist(),
         "metadata": {
         "name": company.get("name") or "Unknown",
         "tagline": company.get("tagline") or "N/A",
         "description": company.get("description") or "N/A",
         "tags": company.get("tags") or [],
         "logo_url": company.get("logo_url") or "na",
         "url": company.get("url") or "N/A",
         "full_text": text
        }
       })

    print(f" Uploading {len(vectors)} fallback/null vectors...")
    index.upsert(vectors=vectors)
    print("Upload complete.")

if __name__ == "__main__":
    main()
