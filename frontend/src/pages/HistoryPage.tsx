import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loadSessions, deleteSession } from '@/types';
import type { ChatSession, Message } from '@/types';

/** Format an ISO date string into a readable label */
function formatDate(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
}

/** Single expanded session view */
function SessionDetail({
  session,
  onClose,
}: {
  session: ChatSession;
  onClose: () => void;
}) {
  return (
    <div className="glass-card rounded-xl overflow-hidden flex flex-col" style={{ maxHeight: '70vh' }}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20 bg-surface-container-low/50 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <span className="material-symbols-outlined text-primary">chat</span>
          <div className="min-w-0">
            <p className="text-label-lg font-semibold text-on-surface truncate">{session.title}</p>
            <p className="text-body-sm text-outline">
              {session.messages.length} messages · {formatDate(session.createdAt)}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="p-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high transition-colors shrink-0"
          aria-label="Close"
        >
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar flex flex-col gap-4">
        {session.messages.map((msg: Message) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center shrink-0 mt-1">
                <span
                  className="material-symbols-outlined text-primary"
                  style={{ fontSize: '16px', fontVariationSettings: "'FILL' 1" }}
                >
                  hexagon
                </span>
              </div>
            )}
            <div
              className={`max-w-[80%] px-4 py-3 rounded-2xl text-body-md leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-primary text-on-primary rounded-tr-sm'
                  : 'bg-surface-container-high text-on-surface rounded-tl-sm'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              <p
                className={`text-xs mt-1 ${
                  msg.role === 'user' ? 'text-on-primary/60' : 'text-outline'
                }`}
              >
                {formatDate(msg.createdAt)}
              </p>
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center shrink-0 mt-1">
                <span
                  className="material-symbols-outlined text-on-secondary-container"
                  style={{ fontSize: '16px', fontVariationSettings: "'FILL' 1" }}
                >
                  person
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function HistoryPage() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<ChatSession[]>(() => loadSessions());
  const [expanded, setExpanded] = useState<ChatSession | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = (id: string) => {
    deleteSession(id);
    setSessions(loadSessions());
    if (expanded?.id === id) setExpanded(null);
    setDeletingId(null);
  };

  return (
    <div className="flex flex-col gap-stack-lg">
      {/* Page header */}
      <div className="mb-2">
        <h2 className="text-display text-on-surface mb-2">History</h2>
        <p className="text-body-lg text-on-surface-variant">
          Your past conversations with CodeSage AI.
        </p>
      </div>

      {/* Empty state */}
      {sessions.length === 0 && (
        <div className="glass-card rounded-xl p-12 flex flex-col items-center justify-center text-center gap-4">
          <span
            className="material-symbols-outlined text-outline"
            style={{ fontSize: '56px', fontVariationSettings: "'FILL' 0" }}
          >
            history
          </span>
          <p className="text-headline-md text-on-surface-variant">No conversations yet</p>
          <p className="text-body-md text-outline max-w-sm">
            Start chatting with your codebase and your conversations will appear here automatically.
          </p>
          <button
            type="button"
            onClick={() => navigate('/chat')}
            className="mt-2 flex items-center gap-2 px-5 py-2.5 bg-primary text-on-primary rounded-xl font-medium hover:opacity-90 transition-opacity"
          >
            <span className="material-symbols-outlined text-lg">chat</span>
            Start a conversation
          </button>
        </div>
      )}

      {/* Session list + optional expanded view */}
      {sessions.length > 0 && (
        <div className="grid grid-cols-12 gap-stack-lg items-start">

          {/* Session list */}
          <div className={`${expanded ? 'col-span-12 lg:col-span-5' : 'col-span-12'} flex flex-col gap-3`}>

            {/* Stats bar */}
            <div className="flex items-center justify-between mb-1">
              <span className="text-body-sm text-outline">
                {sessions.length} conversation{sessions.length !== 1 ? 's' : ''} saved
              </span>
              <button
                type="button"
                onClick={() => navigate('/chat')}
                className="flex items-center gap-1.5 text-body-sm text-primary hover:underline font-medium"
              >
                <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>add</span>
                New chat
              </button>
            </div>

            {sessions.map((session) => (
              <div
                key={session.id}
                className={`glass-card rounded-xl p-4 flex items-start gap-4 cursor-pointer transition-all hover:shadow-md group ${
                  expanded?.id === session.id
                    ? 'border border-primary/50 bg-primary-fixed/10'
                    : 'border border-transparent hover:border-outline-variant/50'
                }`}
                onClick={() => setExpanded(expanded?.id === session.id ? null : session)}
              >
                {/* Icon */}
                <div className="w-10 h-10 rounded-xl bg-primary-container flex items-center justify-center shrink-0">
                  <span
                    className="material-symbols-outlined text-primary"
                    style={{ fontSize: '20px', fontVariationSettings: "'FILL' 1" }}
                  >
                    chat
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-body-md font-semibold text-on-surface truncate">
                    {session.title}
                  </p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-body-sm text-outline">
                      {session.messages.length} message{session.messages.length !== 1 ? 's' : ''}
                    </span>
                    <span className="text-outline/40">·</span>
                    <span className="text-body-sm text-outline">{formatDate(session.updatedAt)}</span>
                  </div>
                  {/* Last message preview */}
                  {session.messages.length > 0 && (
                    <p className="text-body-sm text-on-surface-variant mt-1.5 line-clamp-1">
                      {session.messages[session.messages.length - 1].content}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div
                  className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => e.stopPropagation()}
                >
                  {deletingId === session.id ? (
                    /* Confirm delete */
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => handleDelete(session.id)}
                        className="px-2 py-1 text-xs bg-error text-on-error rounded-lg font-medium hover:opacity-90 transition-opacity"
                      >
                        Delete
                      </button>
                      <button
                        type="button"
                        onClick={() => setDeletingId(null)}
                        className="px-2 py-1 text-xs bg-surface-container-high text-on-surface rounded-lg font-medium hover:bg-surface-container-highest transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setDeletingId(session.id)}
                      className="p-1.5 rounded-lg text-on-surface-variant hover:text-error hover:bg-error-container/20 transition-all"
                      aria-label="Delete session"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
                        delete
                      </span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Expanded session detail */}
          {expanded && (
            <div className="col-span-12 lg:col-span-7">
              <SessionDetail session={expanded} onClose={() => setExpanded(null)} />
            </div>
          )}

        </div>
      )}
    </div>
  );
}
