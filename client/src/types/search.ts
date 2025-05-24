import { ReactNode } from "react";

export interface SearchFilters {
    genres?: string[];
    min_rating?: number;
    max_pages?: number;
    author?: string;
  }
  
  export interface SearchRequest {
    query: string;
    filters?: SearchFilters;
    author?: string;
    genre?: string;
    min_rating?: number;
    max_pages?: number;
    page: number;
    per_page: number;
  }
  
  export interface SearchResult {
    isbn: string;
    title: string;
    author: string;
    genre?: string;
    page_count?: number;
    average_rating?: number;
    cover_url?: string;
  }
  
  export interface SearchResponse {
    results: SearchResult[];
    meta: Record<string, any>; // Flexible dictionary for metadata
  }
  
  export interface TitleSuggestion {
    title: ReactNode;
    author: ReactNode;
    text: string;
    isbn: string;
    score: number;
  }
  
  export interface AuthorSuggestion {
    name: string;
    book_count: number;
  }
  
  export interface PopularSuggestion {
    title: string;
    isbn: string;
    rating: number;
  }
  
  export interface SuggestionResponse {
    titles: TitleSuggestion[];
    authors: AuthorSuggestion[];
    popular: PopularSuggestion[];
  }
  
  export interface SearchHistoryItem {
    query: string;
    timestamp: string;
    is_recent: boolean;
  }
  
  export interface SearchHistoryResponse {
    recent_searches: SearchHistoryItem[];
  }
  
  export interface DeleteHistoryResponse {
    success: boolean;
    message: string;
  }