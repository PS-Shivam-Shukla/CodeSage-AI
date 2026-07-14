import { NavLink } from 'react-router-dom';

interface NavItem {
  icon: string;
  label: string;
  to: string;
}

const NAV_ITEMS: NavItem[] = [
  { icon: 'home',      label: 'Home',         to: '/'            },
  { icon: 'database',  label: 'Repository',   to: '/repository'  },
  { icon: 'chat',      label: 'Chats',        to: '/chat'        },
  { icon: 'history',   label: 'History',      to: '/history'     },
  { icon: 'psychology',label: 'Models',       to: '/models'      },
  { icon: 'hub',       label: 'Vector Store', to: '/vector-store'},
  { icon: 'terminal',  label: 'Logs',         to: '/logs'        },
  { icon: 'key',       label: 'API Keys',     to: '/api-keys'    },
  { icon: 'settings',  label: 'Settings',     to: '/settings'    },
];

const BOTTOM_ITEMS: NavItem[] = [
  { icon: 'person',  label: 'Account', to: '/account' },
  { icon: 'logout',  label: 'Logout',  to: '/logout'  },
];

export function Sidebar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
      isActive
        ? 'bg-secondary-container text-on-secondary-container border-l-4 border-primary'
        : 'text-on-surface-variant hover:bg-surface-container-high'
    }`;

  return (
    <aside className="fixed left-0 top-0 h-screen w-sidebar-width bg-surface-container-low border-r border-outline-variant/20 flex flex-col py-stack-lg gap-stack-md z-50">
      {/* Logo */}
      <div className="px-6 mb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-on-primary shrink-0">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              hexagon
            </span>
          </div>
          <div>
            <h1 className="text-headline-md font-black text-primary leading-tight">CodeSage AI</h1>
            <p className="text-xs text-outline font-medium">v2.4.0-stable</p>
          </div>
        </div>

        {/* Backend status pill */}
        <div className="mt-4 flex items-center gap-2 px-3 py-1.5 bg-secondary-container/30 text-on-secondary-container rounded-full w-fit">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-secondary" />
          </span>
          <span className="text-label-caps font-label-caps uppercase tracking-widest">
            Backend Connected
          </span>
        </div>
      </div>

      {/* Primary navigation */}
      <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto custom-scrollbar">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'} className={linkClass}>
            <span className="material-symbols-outlined">{item.icon}</span>
            <span className="text-label-caps font-label-caps uppercase">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom: account + logout */}
      <div className="px-3 space-y-0.5 border-t border-outline-variant/20 pt-2">
        {BOTTOM_ITEMS.map((item) => (
          <NavLink key={item.to} to={item.to} className={linkClass}>
            <span className="material-symbols-outlined">{item.icon}</span>
            <span className="text-label-caps font-label-caps uppercase">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </aside>
  );
}
