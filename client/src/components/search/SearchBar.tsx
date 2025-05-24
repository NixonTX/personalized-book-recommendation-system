import { useRef, KeyboardEvent, useState } from 'react';
import { SearchBarProps } from './types';
import { classNames } from '@/utils';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { SearchSuggestions } from './SearchSuggestions';
import '../../styles/search.css';

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  onClear,
  loading = false,
  placeholder = 'Search books or authors',
  className,
  suggestions = [],
  onSuggestionsSelect,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] =useState(-1);

  const handleClear = () => {
    onChange('');
    onClear?.();
    inputRef.current?.focus();
    setShowSuggestions(false);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const trimmedValue = value.trim();
      if (trimmedValue) {
        onSubmit(trimmedValue);
        setShowSuggestions(false);
      }
    } else if (e.key === 'Escape') {
      handleClear();
    } else if (e.key === 'ArrowDown' && suggestions.length > 0) {
      e.preventDefault();
      setShowSuggestions(true);
      setSelectedIndex(prev => (prev >= suggestions.length - 1 ? 0 : prev + 1))
    } else if (e.key === 'ArrowUp' && suggestions.length > 0) {
      e.preventDefault();
      setSelectedIndex(prev => (prev <= 0 ? suggestions.length - 1 : prev - 1));
    }
  };

  const handleSuggestionSelect = (suggestion: any) => {
    onSuggestionsSelect?.(suggestion);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  return (
    <div className={classNames('search-bar-container', className)}>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setShowSuggestions(true);
        }
        }
        onKeyDown={handleKeyDown}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}

        placeholder={placeholder}
        className={classNames('search-bar', loading && 'search-bar-loading')}
        aria-label="Search books or authors"
        disabled={loading}
        aria-autocomplete='list'
        aria-controls='search-suggestions'
        aria-expanded={showSuggestions && suggestions.length > 0}
      />
      {value && !loading && (
        <button
          onClick={handleClear}
          className="search-clear-button"
          aria-label="Clear search"
        >
          ✕
        </button>
      )}
      <span className="search-icon" aria-hidden="true">
        <MagnifyingGlassIcon className="h-5 w-5" />
      </span>

      <SearchSuggestions 
        suggestions={suggestions}
        onSelect={handleSuggestionSelect}
        isVisible={showSuggestions && value.length > 0}
        className={className}
      />
    </div>
  );
};