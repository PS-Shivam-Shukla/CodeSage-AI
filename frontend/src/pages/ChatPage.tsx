import { useRef, useState } from 'react';
import { chatService } from '@/services/chat.service';
import { ChatInput } from '@/components/ChatInput';
import { ChatMessage } from '@/components/ChatMessage';
import { RepositoryCard } from '@/components/RepositoryCard';
import { TypingIndicator } from '@/components/ui/TypingIndicator';
import { repositoryService } from '@/services/repository.service';
import type { Message, ChatSession } from '@/types';
import { saveSession } from '@/types';

// ── Suggestion chips shown in the empty state ──────────────────────────────
const SUGGESTIONS = [
  {
    icon: 'account_tree',
    color: 'bg-blue-100 text-blue-600',
    text: 'Give me an overview of this project\'s architecture and main components',
  },
  {
    icon: 'api',
    color: 'bg-purple-100 text-purple-600',
    text: 'List all the API endpoints defined in this repository',
  },
  {
    icon: 'bug_report',
    color: 'bg-red-100 text-red-600',
    text: 'Are there any TODO, FIXME or HACK comments in the codebase?',
  },
  {
    icon: 'schema',
    color: 'bg-green-100 text-green-600',
    text: 'What database models or schemas are defined in this project?',
  },
  {
    icon: 'lock',
    color: 'bg-orange-100 text-orange-600',
    text: 'How is authentication and authorisation handled in this codebase?',
  },
  {
    icon: 'settings',
    color: 'bg-cyan-100 text-cyan-600',
    text: 'What environment variables or configuration values does this project need?',
  },
  {
    icon: 'integration_instructions',
    color: 'bg-pink-100 text-pink-600',
    text: 'How do the different modules or services communicate with each other?',
  },
];

export function ChatPage() {
  // ── chat state ─────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState('');

  // ── active session id for history persistence ──────────────────────────
  const sessionIdRef = useRef<string | null>(null);

  // ── repository panel state ─────────────────────────────────────────────
  const [repoPath, setRepoPath] = useState('');
  const [repoLoading, setRepoLoading] = useState(false);
  const [repoSuccess, setRepoSuccess] = useState(false);
  const [repoError, setRepoError] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = async (question: string) => {
    setChatError('');
    setChatLoading(true);

    const now = new Date().toISOString();

    // Create a new session id on the first message of the conversation
    if (!sessionIdRef.current) {
      sessionIdRef.current = crypto.randomUUID();
    }

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
      createdAt: now,
    };
    const updatedWithUser = [...messages, userMsg];
    setMessages(updatedWithUser);

    try {
      const response = await chatService.sendMessage({ question });
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        createdAt: new Date().toISOString(),
      };
      const finalMessages = [...updatedWithUser, assistantMsg];
      setMessages(finalMessages);

      // Persist the updated session to localStorage
      const session: ChatSession = {
        id: sessionIdRef.current,
        title: question.slice(0, 60) + (question.length > 60 ? '…' : ''),
        messages: finalMessages,
        createdAt: now,
        updatedAt: new Date().toISOString(),
      };
      saveSession(session);
    } catch {
      setChatError('Unable to reach the chat backend. Please try again.');
    } finally {
      setChatLoading(false);
      setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);
    }
  };

  const handleSuggestion = (text: string) => handleSend(text);

  const handleClearChat = () => {
    setMessages([]);
    setChatError('');
    // Reset session so the next message starts a brand-new history entry
    sessionIdRef.current = null;
  };

  const handleIndexRepo = async () => {
    setRepoError('');
    setRepoSuccess(false);
    setRepoLoading(true);
    try {
      await repositoryService.indexRepository({ repository_path: repoPath });
      setRepoSuccess(true);
    } catch {
      setRepoError('Unable to index the repository. Check the path and backend connection.');
    } finally {
      setRepoLoading(false);
    }
  };

  return (
    <>
      {/* Page header */}
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Chat with your code 💬</h2>
        <p className="text-body-lg text-on-surface-variant max-w-2xl">
          Ask anything about your repository. Get intelligent answers instantly.
        </p>
      </div>

      {/* Two-column grid: repository panel (5/12) | chat panel (7/12) */}
      <div className="grid grid-cols-12 gap-stack-lg items-start">

        {/* ── Left: Repository panel ──────────────────────────────────── */}
        <div className="col-span-12 lg:col-span-5">
          <RepositoryCard
            repoPath={repoPath}
            onChange={setRepoPath}
            onSubmit={handleIndexRepo}
            loading={repoLoading}
            success={repoSuccess}
            error={repoError}
          />
        </div>

        {/* ── Right: Chat panel ───────────────────────────────────────── */}
        <div className="col-span-12 lg:col-span-7">
          <div
            className="glass-card flex flex-col rounded-xl shadow-lg overflow-hidden"
            style={{ height: 'calc(100vh - 220px)', minHeight: '600px' }}
          >
            {/* Chat header */}
            <div className="p-4 border-b border-outline-variant/20 flex justify-between items-center bg-surface-container-low/50 shrink-0">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="flex items-center gap-2 px-3 py-1.5 bg-white border border-outline-variant/50 rounded-lg text-body-md font-medium hover:bg-surface-container-low transition-colors"
                >
                  New Conversation
                  <span className="material-symbols-outlined text-lg">expand_more</span>
                </button>
              </div>
              <button
                type="button"
                onClick={handleClearChat}
                className="flex items-center gap-2 px-3 py-1.5 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-lg transition-all text-body-md font-medium"
              >
                <span className="material-symbols-outlined text-lg">delete</span>
                Clear Chat
              </button>
            </div>

            {/* Chat body */}
            <div className="flex-1 overflow-y-auto p-6 custom-scrollbar flex flex-col gap-3">
              {messages.length === 0 ? (
                /* Empty / welcome state */
                <div className="flex flex-col items-center justify-center text-center flex-1 py-8">
                  <div className="w-16 h-16 bg-primary-fixed rounded-2xl flex items-center justify-center text-primary mb-6 animate-pulse">
                    <span
                      className="material-symbols-outlined text-4xl"
                      style={{ fontVariationSettings: "'FILL' 1", fontSize: '36px' }}
                    >
                      hexagon
                    </span>
                  </div>
                  <h4 className="text-headline-lg mb-2">Hi there 👋</h4>
                  <p className="text-body-lg text-on-surface-variant mb-1">I'm CodeSage AI.</p>
                  <p className="text-body-md text-outline mb-10">
                    Your AI assistant for understanding your codebase.
                  </p>

                  {/* Suggestion grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
                    {SUGGESTIONS.map((s) => (
                      <button
                        key={s.text}
                        type="button"
                        onClick={() => handleSuggestion(s.text)}
                        className="p-4 bg-white border border-outline-variant/30 rounded-xl hover:border-primary/50 hover:bg-primary-fixed/20 transition-all text-left flex items-start gap-3 group"
                      >
                        <div
                          className={`p-2 rounded-lg group-hover:scale-110 transition-transform ${s.color}`}
                        >
                          <span
                            className="material-symbols-outlined text-lg"
                            style={{ fontSize: '18px' }}
                          >
                            {s.icon}
                          </span>
                        </div>
                        <span className="text-body-md font-medium">{s.text}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                /* Message list */
                <>
                  {messages.map((msg) => (
                    <ChatMessage
                      key={msg.id}
                      role={msg.role}
                      content={msg.content}
                      onCopy={
                        msg.role === 'assistant'
                          ? () => navigator.clipboard.writeText(msg.content)
                          : undefined
                      }
                    />
                  ))}
                  {chatLoading && <TypingIndicator />}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Error banner */}
            {chatError && (
              <div className="mx-6 mb-2 rounded-xl border border-error/20 bg-error-container/30 px-4 py-2 text-body-sm text-error">
                {chatError}
              </div>
            )}

            {/* Chat input */}
            <div className="shrink-0">
              <ChatInput onSend={handleSend} disabled={chatLoading} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
