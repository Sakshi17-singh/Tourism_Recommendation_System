import React from "react";

export default function SearchResult({ item, onSelect }) {
  return (
    <li
      onClick={() => onSelect(item)}
      className="px-5 py-2 cursor-pointer hover:bg-pink-100 text-gray-700 text-lg"
    >
      {item.name}
    </li>
  );
}
