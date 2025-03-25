import { OpenAI } from "openai";
import { Pinecone } from "@pinecone-database/pinecone";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY,
});

export async function POST(request) {
  try {
    const { query, limit = 10 } = await request.json();

    if (!query) {
      return Response.json({ error: "Query is required" }, { status: 400 });
    }

    // Get embedding for search query
    const embedding = await openai.embeddings.create({
      input: query,
      model: "text-embedding-3-small",
    });

    // Search Pinecone
    const index = pinecone.Index(process.env.PINECONE_INDEX_NAME);
    const results = await index.query({
      vector: embedding.data[0].embedding,
      topK: limit,
      includeMetadata: true,
    });

    const cleanedResults = results.matches.map((match) => ({
      id: match.id,
      score: match.score,
      ...match.metadata,
    }));
    return Response.json({ products: cleanedResults });
  } catch (error) {
    console.error("Search error:", error);
    return Response.json(
      {
        error: "Failed to search companies",
        details: error.message,
      },
      {
        status: 500,
      }
    );
  }
}
