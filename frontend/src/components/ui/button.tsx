import * as React from 'react';
import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  className,
  variant = 'default',
  size = 'md',
  ...props
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 disabled:pointer-events-none disabled:opacity-60 active:scale-95';

  const variants = {
    default: 'bg-primary text-on-primary hover:bg-primary/90 shadow-sm',
    outline:
      'border border-outline-variant text-on-surface hover:bg-surface-container',
    ghost: 'text-on-surface-variant hover:bg-surface-container-high',
    danger:
      'text-error hover:bg-error-container/20 border border-error/20',
  };

  const sizes = {
    sm: 'h-8 px-3 text-body-sm',
    md: 'h-10 px-4 text-body-md',
    lg: 'h-12 px-6 text-body-lg',
  };

  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      {...props}
    />
  );
}
