import { memo, useState } from "react";
import { SearchSuggestionsProps } from "./types";
import { classNames } from "../../utils";
import '../../styles/search.css';

export const SearchSuggestions: React.FC<SearchSuggestionsProps> = memo(({
  suggestions,
  onSelect,
  isVisible,
  className,
}) => {
  const [selectedIndex, setSelectedIndex] = useState(-1);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLLIElement>, suggestion: any, index: number) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      onSelect(suggestion);
      setSelectedIndex(-1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      e.stopPropagation();
      setSelectedIndex((prev) => (prev <= 0 ? suggestions.length - 1 : prev - 1));
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      e.stopPropagation();
      setSelectedIndex((prev) => (prev >= suggestions.length - 1 ? 0 : prev + 1));
    }
  };

  if (!isVisible || !suggestions.length) return null;

  return (
    <ul
      className={classNames('search-suggestions', className)}
      role="listbox"
      aria-label="Search suggestions"
    >
      {suggestions.slice(0, 5).map((suggestion, index) => (
        <li
          key={'isbn' in suggestion ? suggestion.isbn : suggestion.name + index}
          className={classNames(
            'search-suggestion-item',
            index === selectedIndex && 'search-suggestion-item-selected'
          )}
          role="option"
          aria-selected={index === selectedIndex}
          onClick={() => {
            onSelect(suggestion);
            setSelectedIndex(-1);
          }}
          onKeyDown={(e) => handleKeyDown(e, suggestion, index)}
          onMouseEnter={() => setSelectedIndex(index)}
          tabIndex={0}
        >
          {'isbn' in suggestion ? (
            <>
              <span className="search-suggestion-title">{suggestion.title}</span>
              <span className="search-suggestion-author">{suggestion.author}</span>
            </>
          ) : (
            <span className="search-suggestion-author">{suggestion.name}</span>
          )}
        </li>
      ))}
    </ul>
  );
});