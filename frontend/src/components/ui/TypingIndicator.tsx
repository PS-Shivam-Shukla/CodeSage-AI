export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 px-4 py-3 text-body-sm text-on-surface-variant">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
        <div className="flex items-center gap-[3px]">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.3s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary [animation-delay:-0.15s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary" />
        </div>
      </div>
      <p>AI is thinking…</p>
    </div>
  );
}
