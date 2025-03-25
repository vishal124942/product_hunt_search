"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import AnimatedText from "@/components/ui/Animatetext.js";
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
  const [hasSearched, setHasSearched] = useState(false);
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
      setHasSearched(true);
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
    <main className="sm:w-auto sm:h-screen h-screen container mx-auto px-4 py-8">
      <header
        className={`text-center ${
          !hasSearched ? "mb-8" : "mb-6 scale-90"
        } flex flex-col items-center`}
      >
        <h1 className="text-5xl font-bold mb-4">
          <div className="text-gray-900 flex">
            Top
            <div className="bg-red-400  rounded-full w-13 h-13 text-center  text-white">
              P
            </div>
            Hunt
          </div>
        </h1>
        <div className="text-gray-600 text-xl max-w-2xl mx-auto">
          AI-Powered Search for the Product Hunt Products Directory
        </div>
      </header>
      <div className="flex justify-center items-center py-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search for Latest Products.... 🔍"
          className="w-[60%] px-6 py-4 pr-16 border-2 border-gray-200 rounded-full text-lg ocus:outline-none  bg-white shadow-sm"
        />
        <Button onClick={handleSearch} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Search className="h-4 w-4 " />
          )}
          Search
        </Button>
      </div>
      {!hasSearched && (
        <div className=" lg:flex  fit text-center justify-center items-center content-center mb-6 gap-2 -translate-x-[13%]">
          <div className=" text-xl search">Search for</div> <AnimatedText />
        </div>
      )}
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
                <CardTitle className="line-clamp-2 text-xl text-red-400">
                  {product.name}
                </CardTitle>
              </CardHeader>

              <CardContent className="pb-2 flex-grow">
                <p className="text-muted-foreground font-bold line-clamp-3 text-sm">
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

      <footer className="text-center p-4 production md:translate-y-[250px]">
        An{" "}
        <a
          href="https://www.linkedin.com/in/vishal-verma-355a9b1b4/"
          className="text-red-400 "
        >
          Vishal Verma
        </a>{" "}
        Production :)
      </footer>
    </main>
  );
}
