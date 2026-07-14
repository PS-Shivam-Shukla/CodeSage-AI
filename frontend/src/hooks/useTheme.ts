import { useEffect, useState } from 'react';

const THEME_KEY = 'codesage-theme';

/**
 * Thin theme hook – defaults to 'light' to match the MD3 redesign.
 * Persists the choice in localStorage and syncs the <html> class.
 */
export function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window === 'undefined') return 'light';
    const saved = window.localStorage.getItem(THEME_KEY);
    return saved === 'dark' ? 'dark' : 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    // The new design is always light; keep the class toggle for future dark-mode support
    root.classList.toggle('dark', theme === 'dark');
    root.classList.toggle('light', theme === 'light');
    window.localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));

  return { theme, toggleTheme };
}
