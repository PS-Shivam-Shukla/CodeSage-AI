import type { ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  onCopy?: () => void;
}

export function ChatMessage({ role, content, onCopy }: ChatMessageProps) {
  const isAssistant = role === 'assistant';

  return (
    <div
      className={`rounded-xl border p-5 shadow-sm ${
        isAssistant
          ? 'glass-card border-outline-variant/30 self-start'
          : 'bg-primary-fixed/40 border-primary-fixed self-end'
      }`}
    >
      {/* Header row */}
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
              isAssistant
                ? 'bg-primary text-on-primary'
                : 'bg-surface-container-highest text-on-surface'
            }`}
          >
            {isAssistant ? (
              <span
                className="material-symbols-outlined"
                style={{ fontSize: '14px', fontVariationSettings: "'FILL' 1" }}
              >
                smart_toy
              </span>
            ) : (
              <span
                className="material-symbols-outlined"
                style={{ fontSize: '14px', fontVariationSettings: "'FILL' 1" }}
              >
                person
              </span>
            )}
          </div>
          <span className="text-body-sm font-semibold text-on-surface-variant">
            {isAssistant ? 'CodeSage AI' : 'You'}
          </span>
        </div>

        {isAssistant && onCopy && (
          <button
            type="button"
            onClick={onCopy}
            className="inline-flex items-center gap-1.5 rounded-full border border-outline-variant/50 bg-surface-container px-3 py-1 text-xs text-on-surface-variant transition hover:bg-surface-container-high"
          >
            <span className="material-symbols-outlined" style={{ fontSize: '13px' }}>
              content_copy
            </span>
            Copy
          </button>
        )}
      </div>

      {/* Message body – markdown rendered */}
      <div className="prose prose-sm max-w-none break-words text-on-surface leading-relaxed prose-code:rounded-lg prose-code:bg-surface-container prose-code:px-1.5 prose-code:py-0.5 prose-code:text-primary prose-pre:bg-surface-container-high prose-pre:rounded-xl prose-pre:p-0 prose-headings:text-on-surface prose-strong:text-on-surface prose-a:text-primary">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code: ({ inline, className, children, ...props }: any) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={oneLight as any}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    borderRadius: '0.75rem',
                    fontSize: '13px',
                    margin: 0,
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          } as any}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
