import { useEffect, useState } from 'react';
import api from '@/services/api';

interface IndexStatus {
  status: 'ok' | 'not_found' | 'error';
  embeddings?: number;
  segments?: number;
  message?: string;
}

/**
 * Fixed status bar pinned to the bottom of the viewport (right of sidebar).
 * Shows active LLM, vector DB, connection status, and real-time chunk count.
 */
export function StatusFooter() {
  const [indexStatus, setIndexStatus] = useState<IndexStatus | null>(null);

  // Poll /index/status every 10 seconds to keep chunk count live
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const { data } = await api.get<IndexStatus>('/index/status');
        setIndexStatus(data);
      } catch {
        setIndexStatus({ status: 'error', message: 'unreachable' });
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const chunkLabel = (() => {
    if (!indexStatus || indexStatus.status === 'not_found') return '—';
    if (indexStatus.status === 'error') return 'err';
    return indexStatus.embeddings?.toLocaleString() ?? '—';
  })();

  return (
    <footer
      className="fixed bottom-0 z-40 h-8 bg-surface-container-highest flex items-center justify-between px-gutter border-t border-outline-variant/50"
      style={{ left: '280px', width: 'calc(100% - 280px)' }}
    >
      {/* Left stats */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">LLM:</span>
          <span className="font-code-snippet text-xs font-bold text-primary">Meta Llama 3.1 70B</span>
        </div>

        <div className="flex items-center gap-2 cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">Vector:</span>
          <span className="font-code-snippet text-xs font-bold text-primary">ChromaDB</span>
        </div>

        <div className="flex items-center gap-2 cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">Chunks:</span>
          <span className="font-code-snippet text-xs font-bold text-primary">{chunkLabel}</span>
        </div>

        <div className="flex items-center gap-2 cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">Status:</span>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-secondary" />
            <span className="font-code-snippet text-xs font-bold text-secondary">Online</span>
          </div>
        </div>
      </div>

      {/* Right links */}
      <div className="flex items-center gap-6">
        <span className="font-code-snippet text-xs text-on-surface-variant">CodeSage AI © 2026</span>
        <div className="flex items-center gap-4">
          <span className="font-code-snippet text-xs text-outline-variant hover:text-primary transition-colors cursor-pointer">
            Docs
          </span>
          <span className="font-code-snippet text-xs text-outline-variant hover:text-primary transition-colors cursor-pointer">
            API
          </span>
          <span className="font-code-snippet text-xs text-outline-variant hover:text-primary transition-colors cursor-pointer">
            Privacy
          </span>
        </div>
      </div>
    </footer>
  );
}
