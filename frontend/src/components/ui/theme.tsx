import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    const saved = window.localStorage.getItem('codesage-theme');
    setTheme(saved === 'light' ? 'light' : 'dark');
    setMounted(true);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    window.localStorage.setItem('codesage-theme', theme);
  }, [theme]);

  if (!mounted) return null;

  return (
    <button
      type="button"
      onClick={() => setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))}
      className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-slate-900/80 px-4 py-2 text-sm text-slate-200 transition hover:bg-slate-800/90"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
    </button>
  );
}
