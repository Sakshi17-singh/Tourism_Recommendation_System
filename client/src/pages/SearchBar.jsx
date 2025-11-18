import React, { useState, useEffect } from "react";
import { FaSearch } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import SearchResultList from "./SearchResultList";

export default function SearchBar({ placeholder }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (query.trim().length < 1) {
      setResults([]);
      return;
    }

    const fetchData = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/search/?q=${query}`
        );
        const data = await res.json();

        // Take first 5 matches for suggestions (can be random too)
        const suggestions = data.results
          .filter(item =>
            item.name.toLowerCase().startsWith(query.toLowerCase())
          )
          .slice(0, 5);

        setResults(suggestions);
      } catch (err) {
        console.error(err);
        setResults([]);
      }
    };

    const delay = setTimeout(fetchData, 200); // debounce
    return () => clearTimeout(delay);
  }, [query]);

  const handleSearch = () => {
    if (!query.trim()) return;
    navigate(`/searchresult?query=${encodeURIComponent(query)}`);
    setResults([]);
  };

  const handleSelect = (item) => {
    setQuery(item.name);
    navigate(`/searchresult?query=${encodeURIComponent(item.name)}`);
    setResults([]);
  };

  return (
    <div className="relative w-[600px] mt-6 mx-auto">
      <div className="flex border border-gray-400 rounded-full shadow bg-white w-full">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder || "Search places..."}
          className="flex-grow px-4 py-3 outline-none text-gray-700 text-lg rounded-full"
        />

        <button
          onClick={handleSearch}
          className="px-6 bg-black text-white rounded-full text-lg ml-2"
        >
          <FaSearch />
        </button>
      </div>

      {results.length > 0 && (
        <SearchResultList results={results} onSelect={handleSelect} />
      )}
    </div>
  );
}
