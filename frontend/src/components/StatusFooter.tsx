/**
 * Fixed status bar pinned to the bottom of the viewport (right of sidebar).
 * Shows active LLM, vector DB and connection status.
 */
export function StatusFooter() {
  return (
    <footer
      className="fixed bottom-0 z-40 h-8 bg-surface-container-highest flex items-center justify-between px-gutter border-t border-outline-variant/50"
      style={{ left: '280px', width: 'calc(100% - 280px)' }}
    >
      {/* Left stats */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 group cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">LLM:</span>
          <span className="font-code-snippet text-xs font-bold text-primary">Meta Llama 3.1 70B</span>
        </div>

        <div className="flex items-center gap-2 group cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">Vector:</span>
          <span className="font-code-snippet text-xs font-bold text-primary">ChromaDB</span>
        </div>

        <div className="flex items-center gap-2 group cursor-default">
          <span className="font-code-snippet text-xs text-on-surface-variant uppercase">Status:</span>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-secondary" />
            <span className="font-code-snippet text-xs font-bold text-secondary">Online</span>
          </div>
        </div>
      </div>

      {/* Right links */}
      <div className="flex items-center gap-6">
        <span className="font-code-snippet text-xs text-on-surface-variant">CodeSage AI © 2024</span>
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
