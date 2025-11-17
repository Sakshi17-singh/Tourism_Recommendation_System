import React, { useState, useEffect } from "react";
import { FaSearch } from "react-icons/fa";
import SearchResultList from "./SearchResultList";
import SearchResultCard from "./SearchResultCard";

export default function SearchBar({ placeholder }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    if (query.trim().length < 1) {
      setResults([]);
      return;
    }

    const delayDebounce = setTimeout(async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://127.0.0.1:8000/search/?q=${encodeURIComponent(query)}`
        );
        const data = await response.json();
        setLoading(false);

        const combinedResults = data.results || [];

        // Remove duplicates by name
        const uniqueResults = Array.from(
          new Map(combinedResults.map(item => [item.name, item])).values()
        );

        setResults(uniqueResults);
      } catch (error) {
        console.error("Error fetching:", error);
        setLoading(false);
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  const handleSelect = (item) => {
    setQuery(item.name);
    setResults([]);
    setSelectedItem(item);
  };

  const handleSearch = () => {
    if (!query.trim()) return;
    setResults([]);
    setSelectedItem(null);
  };

  return (
    <div className="relative w-[600px] mt-6 mx-auto">
      {/* Search Bar */}
      <div className="flex border border-gray-400 rounded-full shadow-md bg-white w-full overflow-hidden">
        <div className="flex items-center px-4">
          <FaSearch className="text-gray-500 text-lg" />
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder || "Search places..."}
          className="flex-grow px-4 py-3 outline-none text-gray-700 text-lg"
        />

        <button
          onClick={handleSearch}
          className="px-6 bg-black text-white hover:bg-gray-900 transition-all text-lg font-medium"
          style={{ borderTopRightRadius: "9999px", borderBottomRightRadius: "9999px" }}
        >
          Search
        </button>
      </div>

      {/* Suggestions Dropdown */}
      {results.length > 0 && (
        <SearchResultList results={results} onSelect={handleSelect} />
      )}

      {/* Loading */}
      {loading && <p className="text-gray-500 mt-2 text-center">Loading...</p>}

      {/* Selected Item Card */}
      {selectedItem && <SearchResultCard item={selectedItem} />}
    </div>
  );
}
