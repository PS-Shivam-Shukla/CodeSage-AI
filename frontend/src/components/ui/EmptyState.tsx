interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex min-h-[280px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-outline-variant/60 bg-surface-container/30 p-10 text-center">
      <p className="text-headline-md text-on-surface">{title}</p>
      <p className="max-w-lg text-body-md text-on-surface-variant">{description}</p>
    </div>
  );
}
