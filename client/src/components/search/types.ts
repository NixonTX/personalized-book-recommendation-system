import { AuthorSuggestion, TitleSuggestion, SearchHistoryItem } from '../../types/search';

export interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (query: string) => void;
  onClear?: () => void;
  loading?: boolean;
  placeholder?: string;
  className?: string;

  suggestions?: Array<any>;
  onSuggestionsSelect?: (suggestion: any) => void;
}

export interface SearchSuggestionsProps {
  suggestions: (TitleSuggestion | AuthorSuggestion)[];
  onSelect: (suggestion: TitleSuggestion | AuthorSuggestion) => void;
  isVisible: boolean;
  className?: string;
}

export interface SearchHistoryListProps {
  history: SearchHistoryItem[];
  onSelect: (query: string) => void;
  onDelete?: (query: string) => void;
  className?: string;
}