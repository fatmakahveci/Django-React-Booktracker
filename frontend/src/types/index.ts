export interface User {
  id: number;
  email: string;
  user_name: string;
  email_verified: boolean;
  date_joined: string;
}
export interface Book {
  id: number;
  user: number;
  title: string;
  author: string;
  year: number;
  finished: boolean;
  isbn: string;
  cover_url: string;
  notes: string;
  rating: number | null;
  started_on: string | null;
  finished_on: string | null;
  created_at: string;
  updated_at: string;
}
export type BookInput = Omit<Book, "id" | "user" | "created_at" | "updated_at">;
export interface Page<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
export interface Summary {
  total: number;
  finished: number;
  unfinished: number;
}
