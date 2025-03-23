"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2, Search } from "lucide-react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 10 }),
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResults(data.products || []);
    } catch (err) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <main className=" h-screen container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6 text-center">TopHunt</h1>
        <p className="text-2xl font-bold text-center my-4">
          {" "}
          AI-Powered Search for the Product Hunt latest Directory
        </p>

        <div className="flex w-full max-w-lg mx-auto gap-2">
          <Input
            type="text"
            placeholder="Search for products..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 rounded-md"
          />
          <Button onClick={handleSearch} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Search className="h-4 w-4 mr-2" />
            )}
            Search
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive p-4 rounded-md mb-6 max-w-2xl mx-auto">
          <p className="text-center">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : results.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {results.map((product, index) => (
            <Card
              key={product.id}
              className=" h-full flex flex-col hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() =>
                window.open(
                  `https://www.producthunt.com/posts/${product.name}`,
                  "_blank"
                )
              }
            >
              <CardHeader className="pb-2">
                <CardTitle className="line-clamp-2 text-lg text-orange-400">
                  {product.name}
                </CardTitle>
              </CardHeader>
              <CardContent className="pb-2 flex-grow">
                <p className="text-muted-foreground line-clamp-3 text-sm">
                  {product.description || "No description available"}
                </p>
              </CardContent>
              <CardFooter className="pt-2 flex justify-between items-center">
                <div className="flex flex-wrap gap-2 mt-auto">
                  {product.tags.map((tag) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : query.trim() !== "" && !loading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No results found for {query}</p>
        </div>
      ) : null}
      <p className="text-center p-4">
        An <span className="text-orange-500">Vishal Verma</span> Production :)
      </p>
    </main>
  );
}
