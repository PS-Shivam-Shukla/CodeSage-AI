import { NavLink } from 'react-router-dom';

/**
 * Fixed top application bar – sits to the right of the sidebar.
 * Mirrors the design's <header> element exactly.
 */
export function Topbar() {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `font-body-md transition-colors ${
      isActive
        ? 'text-primary font-bold border-b-2 border-primary h-16 flex items-center'
        : 'text-on-surface-variant hover:text-primary flex items-center h-16'
    }`;

  return (
    <header
      className="fixed top-0 z-40 flex justify-between items-center px-8 h-16 bg-surface/80 backdrop-blur-md border-b border-outline-variant/30 shadow-sm"
      style={{ left: '280px', width: 'calc(100% - 280px)' }}
    >
      {/* Left: quick-access nav links */}
      <nav className="flex gap-6 items-center">
        <NavLink to="/models" className={navLinkClass}>
          Models
        </NavLink>
        <NavLink to="/api-keys" className={navLinkClass}>
          API Keys
        </NavLink>
      </nav>

      {/* Right: actions */}
      <div className="flex items-center gap-4">
        <button
          className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-outline-variant text-body-md font-medium hover:bg-surface-container transition-colors"
          type="button"
        >
          <span className="material-symbols-outlined text-lg">help</span>
          Support
        </button>

        <div className="h-8 w-px bg-outline-variant/50" />

        <button
          className="p-2 text-on-surface-variant hover:text-primary transition-colors"
          type="button"
          aria-label="Settings"
        >
          <span className="material-symbols-outlined">settings</span>
        </button>

        {/* User avatar */}
        <div className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container overflow-hidden">
          <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>
            person
          </span>
        </div>
      </div>
    </header>
  );
}
