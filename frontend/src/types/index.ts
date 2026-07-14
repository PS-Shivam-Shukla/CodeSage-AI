export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

/** A persisted chat session stored in localStorage */
export interface ChatSession {
  id: string;
  title: string;          // derived from the first user message (truncated to 60 chars)
  messages: Message[];
  createdAt: string;
  updatedAt: string;
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

// ── localStorage helpers ───────────────────────────────────────────────────

const HISTORY_KEY = 'codesage_chat_history';

/** Load all sessions from localStorage, newest first */
export function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const sessions: ChatSession[] = JSON.parse(raw);
    return sessions.sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    );
  } catch {
    return [];
  }
}

/** Persist a single session (insert or update by id) */
export function saveSession(session: ChatSession): void {
  try {
    const existing = loadSessions();
    const idx = existing.findIndex((s) => s.id === session.id);
    if (idx >= 0) {
      existing[idx] = session;
    } else {
      existing.unshift(session);
    }
    // Keep at most 50 sessions
    localStorage.setItem(HISTORY_KEY, JSON.stringify(existing.slice(0, 50)));
  } catch {
    // storage quota exceeded or private browsing — fail silently
  }
}

/** Delete a session by id */
export function deleteSession(id: string): void {
  try {
    const updated = loadSessions().filter((s) => s.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  } catch {
    // fail silently
  }
}
