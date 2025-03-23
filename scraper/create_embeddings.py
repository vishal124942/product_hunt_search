import json
from pathlib import Path
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTS_PATH = Path("products_data.json")
EMBED_MODEL = "text-embedding-3-small"
PINECONE_INDEX_NAME = "ph-products-index"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_text(company):
    tag_text = " | ".join(company.get("tags", []))
    return f"""{company.get('name', '')}
{company.get('tagline', '')}
{company.get('description', '')}
{tag_text}"""

def is_valid(company):
    return all([
        company.get("name"),
        company.get("tagline"),
        company.get("description"),
        company.get("tags"),
        company.get("logo_url"),
        company.get("url")
    ])

def main():
    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    clean_companies = [c for c in companies if is_valid(c)]
    print(f"📦 Found {len(clean_companies)} fully valid companies")

    client = OpenAI(api_key=OPENAI_API_KEY)
    pc = Pinecone(api_key=PINECONE_API_KEY)

    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    index = pc.Index(PINECONE_INDEX_NAME)

    vectors = []
    for i, company in enumerate(clean_companies, 1):
        text = create_text(company)

        try:
            embedding = client.embeddings.create(
                input=text,
                model=EMBED_MODEL
            ).data[0].embedding
        except Exception as e:
            print(f"❌ Failed to get embedding for {company.get('name')}: {e}")
            continue

        vectors.append({
            "id": f"product-clean-{i}",
            "values": embedding,
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

    print(f"📤 Uploading {len(vectors)} clean vectors...")
    index.upsert(vectors=vectors)
    print("✅ Upload complete.")

if __name__ == "__main__":
    main()