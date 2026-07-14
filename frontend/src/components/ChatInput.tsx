import { type KeyboardEvent, useRef, useState } from 'react';

interface ChatInputProps {
  onSend: (value: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${el.scrollHeight}px`;
  };

  return (
    <div className="p-6 bg-surface-container-lowest border-t border-outline-variant/20">
      <div className="relative group">
        <textarea
          ref={textareaRef}
          rows={3}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          disabled={disabled}
          placeholder="Ask anything about your repository…"
          className="w-full bg-surface-container/50 border border-outline-variant/50 focus:border-primary focus:ring-4 focus:ring-primary/10 rounded-2xl py-4 pl-12 pr-16 resize-none font-body-md transition-all outline-none text-on-surface placeholder:text-outline/60 disabled:opacity-60 disabled:cursor-not-allowed custom-scrollbar"
        />

        {/* Left icon — attach */}
        <div className="absolute left-4 top-4 flex flex-col gap-2">
          <button
            type="button"
            title="Attach file"
            className="text-outline hover:text-primary transition-colors"
            tabIndex={-1}
          >
            <span className="material-symbols-outlined">attach_file</span>
          </button>
        </div>

        {/* Right icons — code blocks + send */}
        <div className="absolute right-4 bottom-4 flex items-center gap-3">
          <button
            type="button"
            title="Code blocks"
            className="text-outline hover:text-primary transition-colors"
            tabIndex={-1}
          >
            <span className="material-symbols-outlined">code_blocks</span>
          </button>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={disabled || !value.trim()}
            title="Send"
            className="w-10 h-10 bg-primary text-on-primary rounded-full flex items-center justify-center hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span
              className="material-symbols-outlined"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              send
            </span>
          </button>
        </div>
      </div>

      <div className="mt-3 flex justify-center">
        <p className="text-[10px] uppercase font-bold tracking-widest text-outline-variant">
          Press Enter to send • Shift + Enter for new line
        </p>
      </div>
    </div>
  );
}
