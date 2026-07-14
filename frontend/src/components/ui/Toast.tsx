interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
}

const tone = {
  success: 'bg-emerald-500/15 text-emerald-200 border-emerald-500/20',
  error: 'bg-rose-500/15 text-rose-200 border-rose-500/20',
  info: 'bg-slate-800/80 text-slate-100 border-slate-700/60',
};

export function Toast({ message, type = 'info' }: ToastProps) {
  return (
    <div className={`rounded-3xl border px-4 py-3 text-sm shadow-soft ${tone[type]}`}>
      {message}
    </div>
  );
}
