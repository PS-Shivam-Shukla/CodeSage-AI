export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

export interface RepositoryIndexResponse {
  status: 'success' | 'error' | 'accepted';
  message: string;
}

export interface ChatResponse {
  answer: string;
}

export interface ChatRequest {
  question: string;
}

export interface IndexRequest {
  repository_path: string;
}
